"""
Pipeline for text processing implementation
"""
import json
import pathlib
import re

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH


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
    path = pathlib.Path(path_to_validate)

    if not path_to_validate.exists():
        raise FileNotFoundError

    if not path.is_dir():
        raise NotADirectoryError

    if not path.glob('*'):
        raise EmptyDirectoryError

    files = {
        "json": 0,
        "pdf": 0,
        "txt": 0
    }
    for file in path.iterdir():
        file_name = file.name
        if not re.match(r'\d+_(raw\.(txt|pdf)|meta\.json)', file_name):
            raise InconsistentDatasetError

        file_number = int(re.findall(r'\d+', file_name)[0])
        current_file_number = files.get(file.suffix)
        if file_number - current_file_number != 1:
            raise InconsistentDatasetError
        files[file.suffix] = file_number

    with open(CRAWLER_CONFIG_PATH) as file:
        config = json.load(file)

    # нужна проверка на порядок, чтобы нумерация начиналась с единицы

    for number_of_files in files.values():
        if number_of_files != config['total_articles_to_find_and_parse']:
            raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    main()
