"""
Pipeline for text processing implementation
"""

from pathlib import Path


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
    path_to_validate = Path(path_to_validate)

    files = [file for file in path_to_validate.glob('*')]
    raw_txt = 0
    meta_json = 0

    if not path_to_validate.exists():
        raise FileNotFoundError

    if not path_to_validate.is_dir():
        raise NotADirectoryError

    if not files:
        raise EmptyDirectoryError

    for file in files:
        if file.suffix == '.txt':
            raw_txt += 1

            if f'{raw_txt}_raw' not in files:
                raise InconsistentDatasetError

        if f'{raw_txt}_raw' not in [file.stem for file in files]:
            raise InconsistentDatasetError

        if file.suffix == '.json':
            meta_json += 1

            if f'{meta_json}_raw' not in files:
                raise InconsistentDatasetError

        if f'{meta_json}_raw' not in [file.stem for file in files]:
            raise InconsistentDatasetError

    if raw_txt != meta_json:
        raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    main()
