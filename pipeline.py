"""
Pipeline for text processing implementation
"""

from pathlib import Path
import re

from pymystem3 import Mystem

from constants import ASSETS_PATH
from core_utils.article import Article

class EmptyDirectoryError(Exception):
    """
    No data to process
    """


class InconsistentDatasetError(Exception):
    """
    Corrupt data: numeration is expected to start from 1 and to be continuous
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
        return f'{self.normalized_form}<{self.tags_mystem}'

    def get_multiple_tagged(self):
        """
        Returns normalized lemma with PyMorphy tags
        """
        return f'{self.normalized_form}<{self.tags_pymorphy}'


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
        path = Path(self.path_to_raw_txt_data)
        for file in path.glob('*'):
            file = file.name
            for elem in file:
                if not elem.isdigit():
                    continue
                article_id = int(elem)
                article = Article(None, article_id)
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
        pass

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path = Path(path_to_validate)
    if not path.exists():
        raise FileNotFoundError
    if not path.is_dir():
        raise NotADirectoryError
    ids = []
    for file in path.iterdir():
        if not file.stem[0].isdigit():
            raise InconsistentDatasetError
        ids.append(int(file.stem[0]))
    if not ids:
        raise EmptyDirectoryError


def main():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    main()
