"""
Pipeline for text processing implementation
"""

from pathlib import Path
import re

# import pymorphy2
# from pymystem3 import Mystem

from constants import ASSETS_PATH
from core_utils.article import Article


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
        pass

    def get_cleaned(self):
        """
        Returns lowercased original form of a token
        """
        pass

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
        path_to_raws = Path(self.path_to_raw_txt_data)
        dataset = [file for file in path_to_raws.rglob('*_raw.txt')]

        for file in dataset:
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
        pass

    def run(self):
        """
        Runs pipeline process scenario
        """
        pass

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        # cleaned_text = ' '.join(re.findall(r'[а-яёА-ЯЁ]+', raw_text))
        # analyzed_cleaned_text = Mystem().analyze(cleaned_text)


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path_to_dataset = Path(path_to_validate)

    if not path_to_dataset.exists():
        raise FileNotFoundError

    if not path_to_dataset.is_dir():
        raise NotADirectoryError

    list_of_txts = list(path_to_dataset.glob('*_raw.txt'))
    list_of_jsons = list(path_to_dataset.glob('*_meta.json'))
    if not len(list_of_txts) == len(list_of_jsons):
        raise InconsistentDatasetError

    txt_indices = [int(txt.parts[-1].split('_')[0]) for txt, json in zip(list_of_txts, list_of_jsons)]
    json_indices = [int(json.parts[-1].split('_')[0]) for txt, json in zip(list_of_txts, list_of_jsons)]

    if sorted(txt_indices) != sorted(json_indices):
        raise InconsistentDatasetError

    if not list(path_to_dataset.iterdir()):
        raise EmptyDirectoryError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)


if __name__ == "__main__":
    main()
