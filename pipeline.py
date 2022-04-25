"""
Pipeline for text processing implementation
"""
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
        self.processed_word = ''
        self.mystem_tags = ''
        self.pymorphy_tags = ''

    def get_cleaned(self):
        """
        Returns lowercased original form of a token
        """
        lowercased = self.original_word.lower()
        return lowercased

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
        self._storage = {}
        self.path = Path(path_to_raw_txt_data)
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path_to_raw = Path(self.path)
        files = list(path_to_raw.glob('*_raw.txt'))
        for file in files:
            article_id = int(file.stem.split('_')[0])
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
        self.corpus_manager = CorpusManager

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
    path_to_validate = Path(path_to_validate)

    if not path_to_validate.exists():
        raise FileNotFoundError

    if not path_to_validate.is_dir():
        raise NotADirectoryError

    files = list(path_to_validate.glob('*'))
    if not files:
        raise EmptyDirectoryError
    roots = [file.stem for file in files]

    json_counter = 0
    raw_counter = 0

    for file in files:
        if file.suffix == '.json':
            json_counter += 1
            if f'{json_counter}_meta' not in roots:
                raise InconsistentDatasetError

        if file.suffix == '.txt':
            raw_counter += 1
            if f'{raw_counter}_raw' not in roots:
                raise InconsistentDatasetError
            with open(file, 'r', encoding='utf-8') as raw_file:
                read_file = raw_file.read()
            if not read_file:
                raise InconsistentDatasetError

    if json_counter != raw_counter:
        raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    main()
