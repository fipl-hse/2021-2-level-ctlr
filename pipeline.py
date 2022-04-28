"""
Pipeline for text processing implementation
"""
import re
from pathlib import Path

from pymystem3 import Mystem

from core_utils.article import Article, ArtifactType
from constants import ASSETS_PATH


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
        return f"{self.normalized_form}<{self.tags_mystem}>"

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
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.path_to_raw_txt_data)
        files = list(path.glob('*_raw.txt'))
        for file in files:
            pattern = re.search(r'\d+', file.name)
            article_id = int(pattern.group(0))
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
            raw_text = article.get_raw_text()
            tokens = self._process(raw_text)
            article_tokens = []
            single_tagged_tokens = []

            for token in tokens:
                article_tokens.append(token.get_cleaned())
                single_tagged_tokens.append(token.get_single_tagged())

            article.save_as(' '.join(article_tokens), ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged_tokens), ArtifactType.single_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        analyzed_text = Mystem().analyze(raw_text.replace("\n", " "))

        tokens = []
        for token in analyzed_text:
            if "analysis" not in token:
                continue
            if not token["analysis"]:
                continue

            morph_token = MorphologicalToken(original_word=token["text"])
            morph_token.normalized_form = token["analysis"][0]["lex"]
            morph_token.tags_mystem = token["analysis"][0]["gr"]

            tokens.append(morph_token)
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
    if not any(path.iterdir()):
        raise EmptyDirectoryError

    for file in path.glob("*.txt"):
        with open(file, 'r', encoding='utf-8') as text_file:
            text = text_file.read()

        raw_data = list(path.glob('*_raw.txt'))
        meta_data = list(path.glob('*_meta.json'))
        if not len(meta_data) == len(raw_data):
            raise InconsistentDatasetError

        if not text:
            raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
