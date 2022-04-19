"""
Pipeline for text processing implementation
"""

from pymystem3 import Mystem
import pymorphy2
from pathlib import Path
import re

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
        self.path_to_raw_txt_data = path_to_raw_txt_data
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path = Path(self.path_to_raw_txt_data)
        for file in path.glob('*'):
            file = file.name
            for element in file:
                if not element.isdigit():
                    continue
                article_id = int(element)
                article = Article(None, article_id)
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
        cleaned_tokens = []
        single_tagged = []
        for article in articles:
            raw_text = article.get_raw_text()
            tokens = self._process(raw_text)
            for token in tokens:
                cleaned_tokens.append(token.get_cleaned())
                single_tagged.append(token.get_single_tagged())
            article.save_as(' '.join(cleaned_tokens), 'cleaned')
            article.save_as(' '.join(single_tagged), 'single_tagged')

        #articles = self.corpus_manager.get_articles().values()
        #for article in articles:
        #    raw_text = article.get_raw_text()
        #    tokens = self._process(raw_text)
        #    cleaned_tokens = []
        #    single_tagged_tokens = []
        #    for token in tokens:
        #        cleaned_tokens.append(token.get_cleaned())
        #        single_tagged_tokens.append(token.get_single_tagged())
        #    article.save_as(' '.join(cleaned_tokens), 'cleaned')
        #    article.save_as(' '.join(single_tagged_tokens), 'single_tagged')

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        cleaned_text = ' '.join(re.findall(r'[а-яА-Яa-zA-Z]+', raw_text))
        analyzed_cleaned_text = Mystem().analyze(cleaned_text)
        tokens = []
        for token in analyzed_cleaned_text:
            if ('analysis' not in token) \
                    or (not token['analysis']) \
                    or ('lex' not in token['analysis'][0]
                        or 'gr' not in token['analysis'][0]):
                continue
            morphological_token = MorphologicalToken(token['text'])
            morphological_token.normalized_form = token['analysis'][0]['lex']
            morphological_token.tags_mystem = token['analysis'][0]['gr']
            tokens.append(morphological_token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    dataset_path = Path(path_to_validate)
    if not dataset_path.exists():
        raise FileNotFoundError
    if not dataset_path.is_dir():
        raise NotADirectoryError
    index = []
    for files in dataset_path.glob('*'):
        if not files.stem[0].isdigit():
            raise InconsistentDatasetError
        index.append(int(files.stem[0]))
    if not index:
        raise EmptyDirectoryError



def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
