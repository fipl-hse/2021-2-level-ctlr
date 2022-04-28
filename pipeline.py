"""
Pipeline for text processing implementation
"""
from constants import  ASSETS_PATH
import re
from core_utils.article import Article

from pathlib import Path


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
        for article in self.corpus_manager.get_articles().values():
            raw_text = article.get_raw_text()
            tokens = self._process(raw_text)


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


    for file in path.glob("*.txt"):
        with open(file, 'r', encoding='utf-8') as text_file:
            text = text_file.read()
        raw_data = list(path.glob('*_raw.txt'))
        meta_data = list(path.glob('*_meta.json'))

        if not len(meta_data) == len(raw_data):
            raise InconsistentDatasetError

        if not text:
            raise InconsistentDatasetError

        pattern = re.match(r'\d+', file.name)
        if not pattern:
            raise InconsistentDatasetError

        article_id = int(pattern.group(0))
        article_id_dict = []

        if article_id < 1:
            raise InconsistentDatasetError
        article_id_dict.append(article_id)

        if not article_id_dict:
            raise EmptyDirectoryError

        previous_article_id = 0
        article_id_sorted = sorted(article_id_dict)

        for article_id in article_id_sorted:
            if article_id - previous_article_id > 1:
                raise InconsistentDatasetError
            previous_article_id = article_id

            if article_id_sorted[0] != 1:
                raise InconsistentDatasetError

            if not text:
                raise InconsistentDatasetError

            name_pattern = re.match(r'\d+', file.name)
            if not name_pattern:
                raise InconsistentDatasetError

            pattern = re.match(r'\d+', file.name)
            article_id = int(pattern.group(0))

            if article_id < 1:
                raise InconsistentDatasetError
            article_id_dict.append(article_id)


        if not article_id_dict:
            raise EmptyDirectoryError

        previous_article_id = 0
        article_id_sorted = sorted(article_id_dict)

        for article_id in article_id_sorted:
            if article_id - previous_article_id > 1:
                raise InconsistentDatasetError
            previous_article_id = article_id

        if article_id_sorted[0] != 1:
            raise InconsistentDatasetError


def main():
    # YOUR CODE HERE

    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
