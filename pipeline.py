"""
Pipeline for text processing implementation
"""
from typing import List

from pathlib import Path
from pymorphy2 import MorphAnalyzer
from pymystem3 import Mystem

from article import Article
from constants import ASSETS_PATH


class EmptyDirectoryError(Exception):
    """
    Custom error
    """


class InconsistentDatasetError(Exception):
    """
    Custom error
    """


class UnknownDatasetError(Exception):
    """
    Custom error
    """


class MorphologicalToken:
    """
    Stores language params for each processed token
    """
    def __init__(self, original_word, normalized_form):
        self.original = original_word
        self.normalized = normalized_form
        self.mystem_tags = ''
        self.pymorphy_tags = ''

    def __str__(self):
        return f'{self.normalized}<{self.mystem_tags}>({str(self.pymorphy_tags)})'


class CorpusManager:
    """
    Works with articles and stores them
    """
    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_raw = path_to_raw_txt_data
        self._storage = self._scan_dataset()

    @staticmethod
    def _scan_dataset():
        """
        Register each dataset entry
        """
        path = Path(ASSETS_PATH)
        arts = {}
        for file in path.iterdir():
            file_name = file.relative_to(path)
            if str(file_name).endswith('_raw.txt'):
                index = str(file_name).split('_raw.txt')[0]
                arts[index] = Article(url=None, article_id=int(index))
        return arts

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus = corpus_manager
        self.current_raw_text = ''

    def run(self):
        """
        Runs pipeline process scenario
        """
        for article in self.corpus.get_articles().values():
            self.current_raw_text = article.get_raw_text()
            tokens = self._process()
            processed = ' '.join(map(str, tokens))
            article.save_processed(processed)

    def _process(self) -> List[type(MorphologicalToken)]:
        mystem = Mystem()
        pymorphy = MorphAnalyzer()
        words = mystem.analyze(self.current_raw_text)
        tokens = []
        for word in words:
            if word.get('analysis') and word.get('text'):
                try:
                    token = MorphologicalToken(original_word=word['text'], normalized_form=word['analysis'][0]['lex'])
                    token.mystem_tags = word['analysis'][0]['gr'].strip()
                    token.pymorphy_tags = pymorphy.parse(word['text'])[0].tag
                    tokens.append(token)
                except (IndexError, KeyError):
                    token = MorphologicalToken(original_word=word['text'], normalized_form=word['text'])
                    if str(pymorphy.parse(word['text'])[0].tag) != 'UNKN':
                        token.pymorphy_tags = pymorphy.parse(word['text'])[0].tag
                    tokens.append(token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path = Path(path_to_validate)
    if not path.exists():
        raise FileNotFoundError
    if not path.is_dir():
        raise NotADirectoryError
    if not list(path.iterdir()):
        raise EmptyDirectoryError
    raws = list(path.glob('*_raw.txt'))
    metas = list(path.glob('*_meta.json'))
    if not len(metas) == len(raws):
        raise InconsistentDatasetError
    meta_indices = sorted(list(map(lambda x: int(x.name.split('_')[0]), metas)))
    raw_indices = sorted(list(map(lambda x: int(x.name.split('_')[0]), raws)))
    if not raw_indices == meta_indices:
        raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)
    print('validated dataset')
    corpus_manager = CorpusManager(ASSETS_PATH)
    print('onto processing')
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
