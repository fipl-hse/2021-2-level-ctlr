"""
Pipeline for text processing implementation
"""

import re
from pathlib import Path
from constants import ASSETS_PATH


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
        pass

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        pass

    def get_articles(self):
        """
        Returns storage params
        """
        pass


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
        pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    tmp_path = Path(path_to_validate)
    if not tmp_path.exists():
        raise FileNotFoundError
    if not tmp_path.is_dir():
        raise NotADirectoryError
    list_of_indexes = []
    for file in tmp_path.iterdir():
        match = re.match(r'\d+', file.name)
        if not match:
            raise InconsistentDatasetError
        if file.stat().st_size == 0:
            raise InconsistentDatasetError
        index = int(match.group(0))
        if index not in list_of_indexes:
            list_of_indexes.append(index)
    if not list_of_indexes:
        raise EmptyDirectoryError
    list_of_indexes_sorted = sorted(list_of_indexes)
    constant_index = 0
    for index in list_of_indexes_sorted:
        if not constant_index and index != 1:
            raise InconsistentDatasetError
        if index - constant_index > 1:
            raise InconsistentDatasetError
        if not Path(str(tmp_path) + '\\' + str(index) + '_raw.txt').is_file() or \
                not Path(str(tmp_path) + '\\' + str(index) + '_meta.json').is_file():
            raise InconsistentDatasetError
        constant_index = index


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)


if __name__ == "__main__":
    main()
