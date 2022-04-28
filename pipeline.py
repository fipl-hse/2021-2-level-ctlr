"""
Pipeline for text processing implementation
"""
from constants import  ASSETS_PATH
from pathlib import Path
import os
import re
from core_utils.article import Article

from pathlib import Path
from pymystem3 import Mystem
import pymorphy2


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
        # self.normalized_form = ''
        # self.tags_mystem = ''
        # self.tags_pymorphy = ''

    def get_cleaned(self):
        """
        Returns lowercased original form of a token
        """
        return self.original_word.lower()

    # def get_single_tagged(self):
    #     """
    #     Returns normalized lemma with MyStem tags
    #     """
    #     pass

    # def get_multiple_tagged(self):
    #     """
    #     Returns normalized lemma with PyMorphy tags
    #     """
    #     pass


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
        for file in path.glob('*.txt'):
            pattern = re.search(r'\d+', file.name)
            if pattern:
                article_id = int(pattern.group(0))
                article = Article(url=None, article_id=article_id)
                self._storage[article_id] = article

    def get_articles(self):
        """
        Returns storage params
        """
        return self._storage
#
#
# class TextProcessingPipeline:
#     """
#     Process articles from corpus manager
#     """
#
#     def __init__(self, corpus_manager: CorpusManager):
#         pass
#
#     def run(self):
#         """
#         Runs pipeline process scenario
#         """
#         pass
#
#     def _process(self, raw_text: str):
#         """
#         Processes each token and creates MorphToken class instance
#         """
#         pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """

    path = Path(path_to_validate)

    if not path.exists():
        raise FileNotFoundError
        # raise NotADirectoryError

    if not path.is_dir():
        raise NotADirectoryError

    # files_dict = []
    #
    # # for i in range(1, 101):
    # #     file_name = str(i)+'_raw.txt'
    # #     files_dict.append(file_name)
    # #     file_for_checking = path_to_validate / file_name
    # #     if file_for_checking not in path_to_validate:
    # #         raise FileNotFoundError
    #
    # # проверить длину списка
    #
    # length = len(path_to_validate.glob('*'))
    #
    # for i in range(length):
    #     file_name = str(i)+'_raw.txt'
    #     file_name1 = str(i)+'_meta.json'
    #
    #     file_for_checking = path_to_validate / file_name
    #     file_for_checking1 = path_to_validate / file_name1
    #     if file_for_checking not in path_to_validate:
    #         raise FileNotFoundError
    #
    #     all_files = path_to_validate.glob('*')
    #     names_dict = []
    #     for file in all_files:
    #         name = file.stem
    #         names_dict.append(name)
    #
    #     if names_dict !=

        children_files_txt = list(path_to_validate.glob('*raw.txt'))
        children_files_json = list(path_to_validate.glob('*.json'))
        children_files = children_files_json + children_files_txt
        if not children_files:
            raise EmptyDirectoryError
        if len(children_files_txt) != len(children_files_json):
            raise InconsistentDatasetError
        file_names = []
        for files_path in children_files:
            file_names.append(files_path.name)
        for i in range(1, int(len(list(children_files)) / 2) + 1):
            if (f'{i}_raw.txt' not in file_names) or (f'{i}_meta.json' not in file_names):
                raise InconsistentDatasetError
        for file in children_files:
            if not Path(file).stat().st_size:
                raise InconsistentDatasetError









def main():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    main()
