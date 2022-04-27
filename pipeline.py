"""
Pipeline for text processing implementation
"""

import json
from pathlib import Path
import re
import os
from constants import ASSETS_PATH

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
    if not os.path.isdir(path_to_validate):
        raise IsADirectoryError

    list_of_files = os.listdir(path_to_validate)
    #print(list_of_files)
    list_of_indexes = []
    for name in list_of_files:
        match = re.match(r'\d+', name)
        if not match:
            raise InconsistentDatasetError("Found a file name that does not correspond to the naming scheme")
        name_path = str(path_to_validate)+'\\'+name
        if not os.path.isfile(name_path):
            raise InconsistentDatasetError("File is empty")
        index = name.index('_')
        if 'raw' in name:
            list_of_indexes.append(int(name[:index]))

    list_of_indexes = sorted(list_of_indexes)
    for index in list_of_indexes[1:]:
        #print(index)
        if index != list_of_indexes[list_of_indexes.index(index)-1]+1:
            raise InconsistentDatasetError

    if len(list_of_files) == 0:
        raise EmptyDirectoryError

    if len(list_of_files) != len(list_of_indexes)*2:
        raise FileNotFoundError


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)


if __name__ == "__main__":
    main()
