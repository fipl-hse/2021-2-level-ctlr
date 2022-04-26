"""
Pipeline for text processing implementation
"""
from pathlib import Path
import re

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
        return f'{self.normalized_form}<{self.tags_mystem}>'

    def get_multiple_tagged(self):
        """
        Returns normalized lemma with PyMorphy tags
        """
        return f'{self.normalized_form}<{self.tags_pymorphy}>({self.tags_pymorphy})'


class CorpusManager:
    """
    Works with articles and stores them
    """

    def __init__(self, path_to_raw_txt_data: str):
        self.path = Path(path_to_raw_txt_data)
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        dataset = list(self.path.glob("*_raw.txt"))
        dataset.sort(key=self._get_file_id)

        for file in dataset:
            file_id = self._get_file_id(file)
            self._storage[file_id] = Article(url=None, article_id=file_id)

    def _get_file_id(self, file):
        pattern = re.compile(r'\d+')
        return int(pattern.match(file.stem).group())

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
            tokenized_text = ' '.join(self._process(article.get_raw_text()))
            article.save_as(text=tokenized_text, kind=ArtifactType.cleaned)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        pattern = re.compile(r'[А-Яа-яA-Za-z ёЁ]')

        for symbol in raw_text:
            if not pattern.match(symbol):
                raw_text = raw_text.replace(symbol, '')

        words = raw_text.split()
        tokens = [MorphologicalToken(word).get_cleaned() for word in words]

        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path = path_to_validate

    if isinstance(path_to_validate, str):
        path = Path(path_to_validate)

    if not path.exists():
        raise FileNotFoundError

    if not path.is_dir():
        raise NotADirectoryError

    if not list(path.glob('**/*')):
        raise EmptyDirectoryError

    needed_file_names = ['_raw', '_meta']

    files = {
        ".json": [],
        ".pdf": [],
        ".txt": []
    }

    pattern = re.compile(r'\d+')

    for file in list(path.glob('*')):

        # check txt files

        # add in dict file id with relevant filename extension
        for file_name_type in needed_file_names:
            if file_name_type in file.stem:
                files.get(file.suffix).append(int(pattern.match(file.stem).group()))
                continue

        if file.suffix == ".txt":
            with file.open(encoding='utf=8') as opened_file:
                file_text = opened_file.read()
                if not file_text:
                    raise InconsistentDatasetError

    # check dataset numeration
    for ids in files.values():
        ids.sort()
        for file_number in range(1, len(ids) - 1):
            if ids[file_number - 1] != file_number:
                raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    main()
