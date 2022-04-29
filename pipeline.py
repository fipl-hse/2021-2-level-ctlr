"""
Pipeline for text processing implementation
"""
import re
from pathlib import Path

import pymorphy2
from pymystem3 import Mystem

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
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path_raw = Path(self.path_to_raw_txt_data)
        article_pattern = re.compile(r'(\d+)')

        for file in path_raw.glob('*_raw.txt'):
            article_id = int(re.search(article_pattern, file.name).group())
            self._storage[article_id] = Article(url=None, article_id=article_id)

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
        articles = CorpusManager.get_articles(self.corpus_manager).values()

        for article in articles:
            raw_text = Article.get_raw_text(article)
            tokens = self._process(raw_text)

            cleaned = []
            single_tagged = []
            multiple_tagged = []
            for token in tokens:
                cleaned.append(token.get_cleaned())
                single_tagged.append(token.get_single_tagged())
                multiple_tagged.append(token.get_multiple_tagged())

            article.save_as(' '.join(cleaned), ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged), ArtifactType.single_tagged)
            article.save_as(' '.join(multiple_tagged), ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        mystem = Mystem()
        morph_analyzer = pymorphy2.MorphAnalyzer()

        raw_text_analysis = mystem.analyze(raw_text.replace('-\n', '').replace('\n', ' '))

        tokens = []
        for single_word_analysis in raw_text_analysis:
            if ('analysis' not in single_word_analysis or
                    not single_word_analysis['analysis'] or
                    'lex' not in single_word_analysis['analysis'][0] or
                    'gr' not in single_word_analysis['analysis'][0]):
                continue

            token = MorphologicalToken(single_word_analysis['text'])
            tokens.append(token)

            analysis = single_word_analysis['analysis']
            token.normalized_form = analysis[0]['lex']
            token.tags_mystem = analysis[0]['gr']

            parses = morph_analyzer.parse(single_word_analysis['text'])
            if not parses:
                continue
            token.tags_pymorphy = parses[0].tag

        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if isinstance(path_to_validate, str):
        path_to_validate = Path(path_to_validate)

    if not path_to_validate.exists():
        raise FileNotFoundError

    if not path_to_validate.is_dir():
        raise NotADirectoryError

    if not any(path_to_validate.iterdir()):
        raise EmptyDirectoryError

    article_ids = []
    pattern = re.compile(r'(\d+)')

    if not all(re.search(pattern, file.name) for file in path_to_validate.glob('*')):
        raise InconsistentDatasetError

    for file in sorted(path_to_validate.glob('*'), key=lambda x: int(re.search(pattern, x.name).group())):
        if file.stat().st_size == 0:
            raise InconsistentDatasetError

        article_ids.append(int(re.search(pattern, file.name).group()))

    for article_id in set(article_ids):
        if (not (path_to_validate / f'{article_id}_meta.json').exists() or
                not (path_to_validate / f'{article_id}_raw.txt').exists()):
            raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
