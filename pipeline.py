"""
Pipeline for text processing implementation
"""
from pathlib import Path
import re
from pymystem3 import Mystem

from constants import ASSETS_PATH
from core_utils.article import Article, ArtifactType


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
        self.original_word = original_word
        self.normalized_form = ''
        self.mystem_tags = ''
        self.pymorphy_tags = ''

    def get_cleaned(self):
        """
        Returns lowercased original form of a token
        """
        return self.original_word.lower()

    def get_single_tagged(self):
        """
        Returns normalized lemma with MyStem tags
        """
        return f'{self.normalized_form}<{self.mystem_tags}>'

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

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.path_to_raw_txt_data)
        for file in path.glob("*.txt"):
            pattern = re.search(r'\d+', file.name)
            if pattern:
                article_id = int(pattern.group(0))
                article = Article(url=None, article_id=article_id)
                self._storage[article_id] = article

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
            raw_text = article.get_raw_text()
            tokens = self._process(raw_text)
            cleaned_tokens = []
            single_tagged_tokens = []
            for token in tokens:
                cleaned_tokens.append(token.get_cleaned())
                single_tagged_tokens.append(token.get_single_tagged())
            article.save_as(*cleaned_tokens, kind=ArtifactType.cleaned)
            article.save_as(*single_tagged_tokens, kind=ArtifactType.single_tagged)
            print(*cleaned_tokens)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        mystem = Mystem()
        analyzed_text = mystem.analyze(raw_text)
        tokens = []
        for analyzed_word in analyzed_text:
            if not analyzed_word.get('analysis'):
                continue
            morphological_token = MorphologicalToken(original_word=analyzed_word.get('text'))
            morphological_token.normalized_form = analyzed_word.get('analysis')[0].get('lex')
            morphological_token.mystem_tags = analyzed_word.get('analysis')[0].get('gr')
            tokens.append(morphological_token)
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

    all_article_ids = []
    for file in path.glob("*.txt"):
        name_pattern = re.match(r'\d+_(raw.txt)', file.name)
        if not name_pattern:
            raise InconsistentDatasetError("Name of file is invalid")

        pattern = re.match(r'\d+', file.name)
        article_id = int(pattern.group(0))
        if article_id < 1:
            raise InconsistentDatasetError("Number of article is invalid")
        all_article_ids.append(article_id)

    if not all_article_ids:
        raise EmptyDirectoryError

    previous_article_id = 0
    sorted_all_ids = sorted(all_article_ids)
    for article_id in sorted_all_ids:
        if article_id - previous_article_id != 1:
            raise InconsistentDatasetError("Incorrect numbering of articles")
        previous_article_id = article_id

    if sorted_all_ids[0] != 1:
        raise InconsistentDatasetError("Numbering should be from 1")


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
