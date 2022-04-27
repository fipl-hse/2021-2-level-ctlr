"""
Pipeline for text processing implementation
"""
import re
from pathlib import Path

from pymystem3 import Mystem
import pymorphy2

from constants import ASSETS_PATH
from core_utils.article import Article, ArtifactType


class EmptyDirectoryError(Exception):
    """
    No data to process
    """


class InconsistentDatasetError(Exception):
    """
    Corrupt data:
        - numeration is expected to start from 1 and to be continuous
        - a number of text files must be equal to the number of meta files
        - text files must not be empty
    """


class MorphologicalToken:
    """
    Stores language params for each processed token
    """

    def __init__(self, original_word):
        self.original_word = original_word
        self.normalized_form = ''
        self.tags_mystem = ''
        self.tags_pymorphy = ''

    def get_cleaned(self):
        """
        Returns lowercased original form of a token
        """
        return self.original_word.lower()

    def get_single_tagged(self):
        """
        Returns normalized lemma with MyStem tags
        """
        return f'{self.normalized_form}<{self.tags_mystem}>'

    def get_multiple_tagged(self):
        """
        Returns normalized lemma with PyMorphy tags
        """
        return f'{self.normalized_form}<{self.tags_mystem}>({self.tags_pymorphy})'


class CorpusManager:
    """
    Works with articles and stores them
    """

    def __init__(self, path_to_raw_txt_data: str):
        self.path_to_raw_txt_data = Path(path_to_raw_txt_data)
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        pattern = re.compile(r'\d+')
        for file in self.path_to_raw_txt_data.iterdir():
            res = pattern.search(file.name)
            if not pattern:
                continue
            article_id = int(res.group(0))
            article = Article(url=None, article_id=article_id)
            self._storage[article_id] = article

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
        self.corpus_manager = corpus_manager

    def run(self):
        """
        Runs pipeline process scenario
        """
        articles = self.corpus_manager.get_articles().values()
        for article in articles:
            raw_text = article.get_raw_text()
            tokens = self._process(raw_text)
            cleaned_tokens = []
            single_tagged_tokens = []
            multiple_tagged_tokens = []
            for token in tokens:
                cleaned_tokens.append(token.get_cleaned())
                single_tagged_tokens.append(token.get_single_tagged())
                multiple_tagged_tokens.append(token.get_multiple_tagged())
            article.save_as(' '.join(cleaned_tokens), kind=ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged_tokens), kind=ArtifactType.single_tagged)
            article.save_as(' '.join(multiple_tagged_tokens), kind=ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        text = raw_text.replace('-\n', '')
        analyzed_text = Mystem().analyze(text)
        morph_analyzer = pymorphy2.MorphAnalyzer()
        tokens = []
        for analyzed_word in analyzed_text:
            if analyzed_word.get('analysis') and analyzed_word.get('text'):
                if analyzed_word['analysis'][0].get('lex') and analyzed_word['analysis'][0].get('gr'):
                    morphological_token = MorphologicalToken(original_word=analyzed_word['text'])
                    morphological_token.normalized_form = analyzed_word['analysis'][0]['lex']
                    morphological_token.tags_mystem = analyzed_word['analysis'][0]['gr']
                    morphological_token.tags_pymorphy = morph_analyzer.parse(analyzed_word['text'])[0].tag
                    tokens.append(morphological_token)
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

    all_ids = []
    pattern = re.compile(r'(\d+)_(?:raw.txt|meta.json|raw.pdf'
                         r'|cleaned.txt|single_tagged.txt'
                         r'|multiple_tagged.txt|image.png)')
    for file in path.iterdir():
        if file.stat().st_size == 0:
            raise InconsistentDatasetError("File is empty")
        res = pattern.match(file.name)
        if not res:
            raise InconsistentDatasetError("Incorrect file name")
        all_ids.append(int(res.group(1)))

    if not all_ids:
        raise EmptyDirectoryError

    ids_without_zero = [i for i in all_ids if i != 0]
    sorted_all_ids = sorted(ids_without_zero)
    previous_article_id = 0
    for article_id in sorted_all_ids:
        if article_id - previous_article_id > 1:
            raise InconsistentDatasetError("Article ids are not consistent")
        previous_article_id = article_id

    if sorted_all_ids[0] != 1:
        raise InconsistentDatasetError("Article ids do not start from 1")

    for num in set(sorted_all_ids):
        raw_path = path / f'{num}_raw.txt'
        meta_path = path / f'{num}_meta.json'
        if not raw_path.exists() or not meta_path.exists():
            raise InconsistentDatasetError(f"There are no meta or raw files for {num} article")


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
