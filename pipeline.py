"""
Pipeline for text processing implementation
"""
from pathlib import Path
import re

import pymorphy2
from pymystem3 import Mystem

from constants import ASSETS_PATH
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
        return f'{self.normalized_form}<{self.tags_mystem}>({self.tags_pymorphy})'


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

        for file in self.path.glob("*_raw.txt"):
            pattern = re.compile(r'\d+')
            file_id = int(pattern.match(file.stem).group())
            self._storage[file_id] = Article(url=None, article_id=file_id)

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
            tokenized_text = self._process(article.get_raw_text())

            cleaned = []
            single_tagged = []
            multiple_tagged = []

            for token in tokenized_text:
                cleaned.append(token.get_cleaned())
                single_tagged.append(token.get_single_tagged())
                multiple_tagged.append(token.get_multiple_tagged())

            article.save_as(' '.join(cleaned), ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged), ArtifactType.single_tagged)
            article.save_as(' '.join(multiple_tagged), ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        cleaned_text = raw_text.replace('-\n', '')

        tokens = []

        result = Mystem().analyze(cleaned_text)
        analyzer = pymorphy2.MorphAnalyzer()

        for single_word in result:

            if 'analysis' not in single_word or not single_word['analysis']:
                continue

            token = MorphologicalToken(single_word['text'])

            token.normalized_form = single_word.get('analysis')[0].get('lex')
            token.tags_mystem = single_word.get('analysis')[0].get('gr')
            token.tags_pymorphy = analyzer.parse(single_word.get('text'))[0].tag

            tokens.append(token)

        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
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

    # pattern = re.compile(r'\d+')
    pattern = re.compile(r'(\d+)(_\w+)')

    for file in list(path.glob('*')):

        # add in dict file id with relevant filename extension
        if pattern.match(file.stem).group(2) in needed_file_names:
            files.get(file.suffix).append(int(pattern.match(file.stem).group(1)))

        # check txt files emptiness
        if '_raw.txt' in file.name:
            if file.stat().st_size == 0:
                raise InconsistentDatasetError

    # check dataset numeration
    files_sorted = {}

    for extension, ids in files.items():
        files_sorted[extension] = sorted(ids)

    for sorted_ids in files_sorted.values():
        for file_number in range(1, len(sorted_ids) + 1):
            if sorted_ids[file_number - 1] != file_number:
                raise InconsistentDatasetError

    # check on balanced dict
    files_values = list(files_sorted.values())
    if files_values[0] != files_values[2]:
        raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
