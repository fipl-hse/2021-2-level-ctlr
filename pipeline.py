"""
Pipeline for text processing implementation
"""


from pymorphy3 import MorphAnalyzer
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
        self.original_word = original_word
        self._normalized_form = ""
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
        self.path_to_raw_text_data = path_to_raw_txt_data
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        for file in self.path_to_raw_text_data.glob("*_raw.txt"):
            index = int(file.name[:-8])
            self._storage[index] = Article(None, index)

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
            text = article.get_raw_text()
            tokens = self._process(text)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        # Linebreaks make Mystem slow and unresponsive.
        tokens = []
        for analysis in Mystem().analyze(raw_text.replace("\n", " ")):
            if "analysis" not in analysis:
                continue
            if not analysis["analysis"]:
                continue
            token = MorphologicalToken(original_word=analysis["text"])
            tokens.append(token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    # Dummy validation
    return None


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
