"""
Pipeline for text processing implementation
"""
from pathlib import Path
import re

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
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path_to_raw_txt_data = Path(self.path_to_raw_txt_data)

        for file in path_to_raw_txt_data.iterdir():
            if '_raw.txt' in file.name:
                article_id = int(re.search(r'\d+_raw', file.name)[0][:-4])
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

            article.save_as(' '.join(cleaned_tokens), ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged_tokens), ArtifactType.single_tagged)
            article.save_as(' '.join(multiple_tagged_tokens), ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        pattern = re.compile(r'[а-яА-Яa-zA-z ё]')
        for symbol in raw_text:
            if not pattern.match(symbol):
                raw_text = raw_text.replace(symbol, '')

        text_analysis = Mystem().analyze(raw_text)
        morph = pymorphy2.MorphAnalyzer()

        processed_tokens = []

        for single_word_analysis in text_analysis:

            if 'analysis' not in single_word_analysis:
                continue

            if not single_word_analysis['analysis']:
                continue

            token = MorphologicalToken(single_word_analysis['text'])
            token.normalized_form = single_word_analysis['analysis'][0]['lex']
            token.tags_mystem = single_word_analysis['analysis'][0]['gr']
            token.tags_pymorphy = morph.parse(single_word_analysis['text'])[0].tag

            processed_tokens.append(token)

        return processed_tokens


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

    if len(list(path_to_validate.iterdir())) == 0:
        raise EmptyDirectoryError

    counter_txt = 0
    counter_meta = 0

    for file in sorted(path_to_validate.iterdir(), key=lambda x: int(x.name[:x.name.find('_')])):
        if file.name.endswith('raw.txt'):
            counter_txt += 1

            if f'{counter_txt}_raw' not in file.name:
                raise InconsistentDatasetError

            with open(file, 'r', encoding='utf-8') as current_file:
                text = current_file.read()
            if not text:
                raise InconsistentDatasetError

        if file.name.endswith('meta.json'):
            counter_meta += 1

    if counter_txt != counter_meta:
        raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
