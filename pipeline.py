"""
Pipeline for text processing implementation
"""

from pathlib import Path
import re

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
        self._storage = {}
        self.path = Path(path_to_raw_txt_data)

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        files = self.path.glob("*")
        pattern = re.compile(r'[0-9]+')
        for texts in files:
            if "_raw.txt" in texts.name:
                article_id = int(pattern.search(texts.name).group(0))
                self._storage[article_id] = Article(url=None, article_id=article_id)

    def get_articles(self):
        """
        Returns storage params
        """
        self._scan_dataset()
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
        articles = self.corpus_manager.get_articles()

        for article in articles.values():
            article_text = article.get_raw_text()
            cleaned_tokens = []
            single_tagged_tokens = []
            multiple_tagged_tokens = []

            for token in self._process(article_text):
                cleaned_tokens.append(token.get_cleaned())
                single_tagged_tokens.append(token.get_single_tagged())
                multiple_tagged_tokens.append(token.get_multiple_tagged())

            article.save_as(' '.join(cleaned_tokens), ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged_tokens), ArtifactType.single_tagged)
            article.save_as(' '.join(multiple_tagged_tokens), ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        letters = re.compile(r'[A-Za-zА-Яа-яё]')
        normal_text = ""
        for symbol in raw_text:
            if letters.match(symbol) or symbol.isspace():
                normal_text += symbol

        analyzed_text = Mystem().analyze(normal_text)
        morphs = pymorphy2.MorphAnalyzer()

        tokens = []
        for token in analyzed_text:
            if not token.get("analysis"):
                continue
            if "analysis" not in token:
                continue
            if "LATN" in token['analysis'][0]['gr']:
                continue
            morph_token = MorphologicalToken(original_word=token['text'])
            morph_token.normalized_form = token['analysis'][0]['lex']
            morph_token.tags_mystem = token['analysis'][0]['gr']
            morph_token.tags_pymorphy = morphs.parse(token['text'])[0].tag
            tokens.append(morph_token)
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

    data = list(path_to_validate.glob('*'))

    if not data:
        raise EmptyDirectoryError

    number_of_texts = 0
    number_of_metas = 0

    pattern = re.compile(r'[0-9]+')
    for file in sorted(list(path_to_validate.glob('*')), key=lambda x: int(pattern.search(x.name).group(0))):
        if "_raw.txt" in file.name:
            with open(file, 'r', encoding='utf-8') as text_file:
                text = text_file.read()
                if not text:
                    raise InconsistentDatasetError
            file_id = int(pattern.search(file.name).group(0))
            if file_id == 0 or file_id - number_of_texts > 1 or \
                    not (path_to_validate / f'{file_id}_raw.txt').is_file() or \
                    not (path_to_validate / f'{file_id}_meta.json').is_file():
                raise InconsistentDatasetError
            number_of_texts += 1

        if "_meta.json" in file.name:
            number_of_metas += 1

    if number_of_texts != number_of_metas:
        raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
