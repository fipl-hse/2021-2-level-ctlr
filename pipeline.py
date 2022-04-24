"""
Pipeline for text processing implementation
"""
import re

from pathlib import Path
from pymystem3 import Mystem

from constants import ASSETS_PATH
from core_utils.article import Article


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
        self.normalized_form = ''
        self.tags_mystem = ''
        self.tags_pymorphy = ''
        self.original_word = 'original_token'

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
        pass


class CorpusManager:
    """
    Works with articles and stores them
    """

    def __init__(self, path_to_raw_txt_data: str):
        self._storage = {}
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        paths_to_files = list(Path(self.path_to_raw_txt_data).glob('*_raw.txt'))
        id_template = re.compile(r'\d+')
        for file_path in paths_to_files:
            file_id = int(id_template.search(file_path.name).group())
            article_object = Article(url=None, article_id=file_id)
            self._storage[file_id] = article_object

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
        for article_item in self.corpus_manager.get_articles().values():
            list_of_tokens = self._process(article_item.get_raw_text())

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        article_text = raw_text.replace('-\n', '')
        for symbol in ['\n', '\r']:
            article_text = article_text.replace(symbol, ' ')
        m_tokens_list = []
        analyzed_text_mystem = Mystem().analyze(article_text)
        for analyzed_word in analyzed_text_mystem:
            if analyzed_word['text'] == ' ':
                continue
            original_word = analyzed_word['text']
            token = MorphologicalToken(original_word)
            if 'analysis' not in analyzed_word.keys():
                continue
            if not analyzed_word['analysis']:
                continue
            if 'lex' not in analyzed_word['analysis'][0].keys():
                continue
            token.normalized_form = analyzed_word['analysis'][0].get('lex')
            if 'gr' not in analyzed_word['analysis'][0].keys():
                continue
            token.tags_mystem = analyzed_word['analysis'][0].get('gr')
            m_tokens_list.append(token)
        return m_tokens_list


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path_to_validate = Path(path_to_validate)
    if not path_to_validate.exists():
        raise FileNotFoundError
    if not path_to_validate.is_dir():
        raise NotADirectoryError
    children_files = list(path_to_validate.glob('*raw.txt'))
    children_files.extend(list(path_to_validate.glob('*.json')))
    if not children_files:
        raise EmptyDirectoryError
    file_names = []
    for files_path in children_files:
        file_names.append(files_path.name)
    if len(file_names) % 2 != 0:
        raise InconsistentDatasetError
    for i in range(1, int(len(list(children_files)) / 2) + 1):
        if (f'{i}_raw.txt' not in file_names) or (f'{i}_meta.json' not in file_names):
            raise InconsistentDatasetError
    for file in children_files:
        with open(file, 'r', encoding='utf-8') as text_file:
            text = text_file.read()
        if not text:
            raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
