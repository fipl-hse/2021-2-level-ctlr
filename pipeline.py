"""
Pipeline for text processing implementation
"""

import re
from pathlib import Path

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
        pass
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
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        list_of_indexes = []
        for file in Path(self.path_to_raw_txt_data).iterdir():
            match = re.match(r'\d+', file.name)
            list_of_indexes.append(int(match.group(0)))
        for index in set(list_of_indexes):
            article = Article(url=None, article_id=index)
            self._storage[index] = article

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
        articles = self.corpus_manager.get_articles().values()
        for article in articles:
            text = article.get_raw_text()
            tokens_proc = self._process(text)
            tokens_cool = []
            tokens_s_t = []
            tokens_m_t = []
            for processed_token in tokens_proc:
                tokens_cool.append(processed_token.get_cleaned())
                tokens_s_t.append(processed_token.get_single_tagged())
                tokens_m_t.append(processed_token.get_multiple_tagged())
            article.save_as(' '.join(tokens_cool), ArtifactType.cleaned)
            article.save_as(' '.join(tokens_s_t), ArtifactType.single_tagged)
            article.save_as(' '.join(tokens_m_t), ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        text = raw_text.replace('-\n', '')
        text_anal = Mystem().analyze(text)
        tokens = []
        morph = pymorphy2.MorphAnalyzer()
        for inf in text_anal:
            original_word = inf['text']
            if not inf.get('analysis') or \
                    'lex' not in inf['analysis'][0] or 'gr' not in inf['analysis'][0]:
                continue
            morphological_token = MorphologicalToken(original_word=original_word)
            morphological_token.normalized_form = inf['analysis'][0]['lex']
            morphological_token.tags_mystem = inf['analysis'][0]['gr']
            pars = morph.parse(original_word)[0]
            morphological_token.tags_pymorphy = pars.tag
            tokens.append(morphological_token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    tmp_path = Path(path_to_validate)
    if not tmp_path.exists():
        raise FileNotFoundError
    if not tmp_path.is_dir():
        raise NotADirectoryError
    list_of_indexes = []
    for file in tmp_path.iterdir():
        match = re.match(r'\d+', file.name)
        if not match:
            raise InconsistentDatasetError
        if file.stat().st_size == 0:
            raise InconsistentDatasetError
        index = int(match.group(0))
        if index not in list_of_indexes:
            list_of_indexes.append(index)
    if not list_of_indexes:
        raise EmptyDirectoryError
    list_of_indexes_sorted = sorted(list_of_indexes)
    constant_index = 0
    for index in list_of_indexes_sorted:
        if not constant_index and index != 1:
            raise InconsistentDatasetError
        if index - constant_index > 1:
            raise InconsistentDatasetError
        if not (tmp_path / f'{index}_raw.txt').is_file() or \
                not (tmp_path / f'{index}_meta.json').is_file():
            raise InconsistentDatasetError
        constant_index = index


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    text_processing_pipe_of_insight = TextProcessingPipeline(corpus_manager)
    text_processing_pipe_of_insight.run()

if __name__ == "__main__":
    main()
