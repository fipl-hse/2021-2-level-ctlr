"""
Pipeline for text processing implementation
"""
import os
from os import walk
from pathlib import Path
import re
import string
from constants import ASSETS_PATH
from core_utils.article import Article
from core_utils.article import ArtifactType


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
        self.path_to_raw_txt_data = Path(path_to_raw_txt_data)
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        _txt_extension = ".txt"
        _txt_files = [fn for fn in os.listdir(self.path_to_raw_txt_data)
                      if fn.endswith(_txt_extension) and 'cleaned' not in fn]

        for filename in _txt_files:
            _article_id = _txt_files.index(filename) + 1
            if _article_id < len(_txt_files) + 1:
                self._storage[_article_id] = Article(url=None, article_id=_article_id)

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
        pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    _validate_path(path_to_validate)
    filenames = _get_file_names(path_to_validate)

    _validate_filenames(filenames)
    _validate_files(filenames, ASSETS_PATH)

    _check_consistency(path_to_validate)


def _validate_path(path_to_validate):

    if not isinstance(path_to_validate, Path):
        raise FileNotFoundError("Must be path")

    env_path = Path(path_to_validate)

    if not os.path.exists(path_to_validate) or os.path.getsize(path_to_validate) <= 0:
        raise FileNotFoundError("File not exists")

    if not env_path.is_dir():
        raise NotADirectoryError("File not exists")

    if len(os.listdir(path_to_validate)) == 0:
        raise EmptyDirectoryError("directory is empty")


def _validate_filenames(list_to_validate):
    for filename in list_to_validate:
        _is_extension_correct = filename.endswith(".json") or filename.endswith(".txt")
        _is_name_length_valid = len(filename) > 4
        _first_symbol = filename[0]
        _is_name_begins_correctly = _first_symbol.isdigit() and "_" in filename
        _is_whole_name_correct = _is_extension_correct and _is_name_length_valid and _is_name_begins_correctly

        if not _is_whole_name_correct:
            raise InconsistentDatasetError("Filename should be correct")


def _validate_files(filenames, basepath):
    for filename in filenames:
        path = basepath / filename

        if path.exists():
            with open(path, 'r', encoding='utf-8') as the_file:
                text = the_file.read()
                if not text:
                    raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    main()
