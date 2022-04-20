"""
Pipeline for text processing implementation
"""
from pymorphy2 import MorphAnalyzer
from pymystem3 import Mystem

from pathlib import Path
import re

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
        self.normalized_form = ""
        self.mystem_tags = ""
        self.pymorphy_tags = ""

    def get_cleaned(self):
        """
        Returns lowercased original form of a token
        """
        return self.original_word.lower()

    def get_single_tagged(self):
        """
        Returns normalized lemma with MyStem tags
        """
        pass

    def get_multiple_tagged(self):
        """
        Returns normalized lemma with PyMorphy tags
        """
        pass


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

        for file in path.rglob('*_raw.txt'):
            article_id = int(file.parts[-1].split('_')[0])
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
        tokens = []
        for article in articles:
            article_raw_text = article.get_raw_text()

            for token in self._process(article_raw_text):
                tokens.append(token.get_cleaned())

            article.save_as(' '.join(tokens), ArtifactType.cleaned)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """

        text = re.sub(r"[^а-я\s]", "", raw_text)
        tokens = text.split()

        morphological_tokens = [MorphologicalToken(original_word=word) for word in tokens]

        return morphological_tokens


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

    meta = []
    raw = []
    for file in path.rglob('*.json'):
        meta.append(file.parts[-1].split('_')[0])
    for file in path.rglob('*_raw.txt'):
        raw.append(file.parts[-1].split('_')[0])
    if meta != raw:
        raise InconsistentDatasetError




def main():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    main()
