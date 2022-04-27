"""
Pipeline for text processing implementation
"""
import re
from collections import namedtuple
from pathlib import Path
from typing import List

from pymorphy2 import MorphAnalyzer
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
        self.normalized_form = ""
        self.tags_mystem = ""
        self.tags_pymorphy = ""

    def get_cleaned(self):
        """
        Returns lowercased original form of a token
        """
        return self.original_word.lower()

    def get_single_tagged(self):
        """
        Returns normalized lemma with MyStem tags
        """
        tagged_token = f"{self.normalized_form}<{self.tags_mystem}>"
        return tagged_token

    def get_multiple_tagged(self):
        """
        Returns normalized lemma with PyMorphy tags
        """
        tagged_token = f"{self.normalized_form}<{self.tags_mystem}>({self.tags_pymorphy})"
        return tagged_token


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

        for idx in path.glob(r"*_raw.txt"):
            article_id = int(re.match(r"^\d+", idx.parts[-1]).group())
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
        self.corpus_manager = corpus_manager

    def run(self):
        """
        Runs pipeline process scenario
        """
        for article in self.corpus_manager.get_articles().values():
            processed_text = self._process(article.get_raw_text())
            article.save_as(
                text=" ".join(list(map(MorphologicalToken.get_cleaned, processed_text))),
                kind=ArtifactType.cleaned
            )
            article.save_as(
                text=" ".join(list(map(MorphologicalToken.get_single_tagged, processed_text))),
                kind=ArtifactType.single_tagged
            )
            article.save_as(
                text=" ".join(list(map(MorphologicalToken.get_multiple_tagged, processed_text))),
                kind=ArtifactType.multiple_tagged
            )

    def _process(self, raw_text: str) -> List[type(MorphologicalToken)]:
        """
        Processes each token and creates MorphToken class instance
        """
        clean_text = re.findall(r"[А-Яа-яё]+", re.sub(r"-\n", "", raw_text))
        text = " ".join(clean_text)

        mystem_analyzer = Mystem().analyze(text)
        pymorphy_analyzer = MorphAnalyzer()

        morph_tokens = []
        for word in mystem_analyzer:
            if word.get('analysis') and word.get('text'):
                if word['analysis'][0].get('lex') and word['analysis'][0].get('gr'):
                    morph_token = MorphologicalToken(word['text'])
                    morph_token.normalized_form = word['analysis'][0]['lex']
                    morph_token.tags_mystem = word['analysis'][0]['gr']
                    morph_tokens.append(morph_token)

        for token in morph_tokens:
            pymorphy_tokens = pymorphy_analyzer.parse(token.original_word)
            if pymorphy_tokens:
                token.tags_pymorphy = pymorphy_tokens[0].tag

        return morph_tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path = Path(path_to_validate)
    Validation = namedtuple('Validation', ['success', 'error'])

    is_exists = path.exists()
    is_dir = path.is_dir()
    txt_files = list(path.rglob('*_raw.txt'))
    json_files = list(path.rglob('*_meta.json'))

    txt_ids = list(map(lambda file: int(file.parts[-1].split('_')[0]), txt_files))
    json_ids = list(map(lambda file: int(file.parts[-1].split('_')[0]), json_files))
    is_consistent_txt = len(txt_ids) == len(txt_files) and set(txt_ids) == set(range(min(txt_ids), max(txt_ids) + 1))
    is_consistent_json = (
            len(json_ids) == len(json_files) and
            set(json_ids) == set(range(min(json_ids), max(json_ids) + 1))
    )

    validations = (
        Validation(is_exists, FileNotFoundError),
        Validation(is_dir, NotADirectoryError),
        Validation(txt_files and json_files, EmptyDirectoryError),
        Validation(is_consistent_txt and is_consistent_json, InconsistentDatasetError),
    )

    for test in validations:
        if not test.success:
            raise test.error()


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
