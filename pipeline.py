"""
Pipeline for text processing implementation
"""

import re

from pathlib import Path
from pymystem3 import Mystem
import pymorphy2

from core_utils.article import Article
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
        for file in path.glob('*.txt'):
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
        for article in self.corpus_manager.get_articles().values():
            tokens = self._process(article.get_raw_text())
            tokens_for_article = []
            single_tagged_tokens = []
            multiple_tagged_tokens = []
            for token in tokens:
                tokens_for_article.append(token.get_cleaned())
                single_tagged_tokens.append(token.get_single_tagged())
                multiple_tagged_tokens.append(token.get_multiple_tagged())
            article.save_as(' '.join(tokens_for_article), kind='cleaned')
            article.save_as(' '.join(single_tagged_tokens), kind='single_tagged')
            article.save_as(' '.join(multiple_tagged_tokens), kind='multiple_tagged')

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        cleaned_text = raw_text.replace('-\n', '')
        for symbol in ['\n', '\r', '-']:
            cleaned_text = cleaned_text.replace(symbol, ' ')
        analyzed_text = Mystem().analyze(cleaned_text)
        morph = pymorphy2.MorphAnalyzer()
        tokens = []
        for token in analyzed_text:
            if token['text'] == ' ':
                continue
            if 'analysis' not in token.keys():
                continue
            if not token['analysis']:
                continue
            if 'lex' not in token['analysis'][0] or 'gr' not in token['analysis'][0]:
                continue
            morphological_token = MorphologicalToken(original_word=token['text'])
            morphological_token.normalized_form = token['analysis'][0].get('lex')
            morphological_token.tags_mystem = token['analysis'][0].get('gr')
            tokens.append(morphological_token)
            morphological_token.tags_pymorphy = morph.parse(token['text'])[0].tag
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
        with open(file, 'r', encoding='utf-8') as text_file:
            text = text_file.read()
        raws = list(path.glob('*_raw.txt'))
        metas = list(path.glob('*_meta.json'))
        if not len(metas) == len(raws):
            raise InconsistentDatasetError
        if not text:
            raise InconsistentDatasetError
        name_pattern = re.match(r'\d+', file.name)
        if not name_pattern:
            raise InconsistentDatasetError
        pattern = re.match(r'\d+', file.name)
        article_id = int(pattern.group(0))
        if article_id < 1:
            raise InconsistentDatasetError
        all_article_ids.append(article_id)
    if not all_article_ids:
        raise EmptyDirectoryError
    previous_article_id = 0
    sorted_all_ids = sorted(all_article_ids)
    for article_id in sorted_all_ids:
        if article_id - previous_article_id > 1:
            raise InconsistentDatasetError
        previous_article_id = article_id
    if sorted_all_ids[0] != 1:
        raise InconsistentDatasetError

def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
