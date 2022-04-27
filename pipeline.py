"""
Pipeline for text processing implementation
"""
import re
from pathlib import Path

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
        self.normalized_form = None
        self.tags_mystem = None
        self.tags_pymorphy = None

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
        self.path = Path(path_to_raw_txt_data)
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        dataset = list(self.path.glob('*_raw.txt'))
        dataset.sort(key=self._extract_file_id)
        for file in dataset:
            file_id = self._extract_file_id(file)
            self._storage[file_id] = Article(url=None, article_id=file_id)

    def _extract_file_id(self, file):
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
        tokens = []
        letters = re.compile(r'[А-Яа-яA-Za-z ёЁ]')
        for character in raw_text:
            if letters.match(character) is None:
                raw_text = raw_text.replace(character, '')
        words = raw_text.split()
        for word in words:
            tokens.append(MorphologicalToken(word).get_cleaned())
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    if isinstance(path_to_validate, str):
        path_to_validate = Path(path_to_validate)
    if not path_to_validate.exists():
        raise FileNotFoundError
    if not path_to_validate.is_dir():
        raise NotADirectoryError
    if not list(path_to_validate.glob('**/*')):
        raise EmptyDirectoryError
    if check_dataset_numeration(path_to_validate) == -1:
        raise InconsistentDatasetError
    if check_txt_files(path_to_validate) == -1:
        raise InconsistentDatasetError


def check_dataset_numeration(dataset_path):
    """
    Checks that the dataset is valid
    """
    files_to_check = ['_raw', '_meta']
    files = {
        '.json': [],
        '.txt': [],
        '.pdf': []
    }
    pattern = re.compile(r'\d+')

    for file in list(dataset_path.glob('*')):
        for file_name_type in files_to_check:
            if file_name_type in file.stem:
                files.get(file.suffix).append(int(pattern.match(file.stem).group()))
                continue

    for files_suffix, ids_list in files.items():
        ids_list.sort()
        for file_number in range(1, len(ids_list) - 1):
            if ids_list[file_number - 1] != file_number:
                print(f'Missing file № {file_number} with {files_suffix} suffix')
                return -1

    files_ids = list(files.values())
    if files_ids[0] != files_ids[1]:
        return -1
    return 0


def check_txt_files(dataset_path):
    for file in list(dataset_path.glob('*')):
        if '_raw.txt' in file.name:
            file_content = file.open('r', encoding='utf-8')
            file_text = file_content.read()
            file_content.close()
            if not file_text:
                return -1
    return 0


def main():
    print('STARTING PROGRAM...\nVALIDATING DATASET...')
    validate_dataset(ASSETS_PATH)
    print('DATASET IS CORRECT.\nCREATING CORPUS MANAGER ABSTRACTION...')
    corpus_manager = CorpusManager(ASSETS_PATH)
    print('DONE.\nCREATING PIPELINE INSTANCE...')
    pipe = TextProcessingPipeline(corpus_manager)
    print('DONE.\nRUNNING TEXT PROCESSING ON COLLECTED FILES...')
    pipe.run()
    print('DONE.')


if __name__ == "__main__":
    main()
