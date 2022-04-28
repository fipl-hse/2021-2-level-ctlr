"""
Pipeline for text processing implementation
"""

from pathlib import Path
import re

from pymystem3 import Mystem
import pymorphy2

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
        articles = CorpusManager.get_articles(self.corpus_manager).values()
        for article in articles:
            raw_text = Article.get_raw_text(article)
            tokens = self._process(raw_text)
            tokens_for_article = []
            single_tagged_tokens = []
            multiple_tagged_tokens = []
            for token in tokens:
                tokens_for_article.append(token.get_cleaned())
                single_tagged_tokens.append(token.get_single_tagged())
                multiple_tagged_tokens.append(token.get_multiple_tagged())
            article.save_as(' '.join(tokens_for_article), ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged_tokens), ArtifactType.single_tagged)
            article.save_as(' '.join(multiple_tagged_tokens), ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        pattern = re.compile(r'[а-яА-Яa-zA-z ё]')
        for symbol in raw_text:
            if not pattern.match(symbol):
                raw_text = raw_text.replace(symbol, '')
        text_analysis = Mystem().analyze(raw_text)
        morph = pymorphy2.MorphAnalyzer()
        tokens = []
        for word in text_analysis:
            if 'analysis' not in word:
                continue
            if not word['analysis']:
                continue
            token = MorphologicalToken(word['text'])
            token.normalized_form = word['analysis'][0]['lex']
            token.tags_mystem = word['analysis'][0]['gr']
            token.tags_pymorphy = morph.parse(word['text'])[0].tag
            tokens.append(token)
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
    if len(list(path_to_validate.glob('*'))) == 0:
        raise EmptyDirectoryError
    texts = 0
    meta_data = 0
    for file in sorted(path_to_validate.glob('*'), key=lambda x: int(x.name[:x.name.find('_')])):
        if file.name.endswith('raw.txt'):
            texts += 1
            if f'{texts}_raw' not in file.name:
                raise InconsistentDatasetError
            with open(file, 'r', encoding='utf-8') as current:
                text = current.read()
            if not text:
                raise InconsistentDatasetError
        if file.name.endswith('meta.json'):
            meta_data += 1
    if texts != meta_data:
        raise InconsistentDatasetError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
