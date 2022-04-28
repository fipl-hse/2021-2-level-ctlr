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
        pass


class CorpusManager:
    """
    Works with articles and stores them
    """

    def __init__(self, path_to_raw_txt_data: str):
        self._storage = {}
        self.path = Path(path_to_raw_txt_data)
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        path_to_raw = self.path

        for file in path_to_raw.glob('*_raw.txt'):
            pattern = re.compile(r'\d+')
            article_id = int(pattern.search(file.name).group(0))
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
        articles = self.corpus_manager.get_articles().values()
        for article in articles:
            raw_text = article.get_raw_text()
            tokens = self._process(raw_text)
            cleaned_tokens = []
            single_tagged_tokens = []
            for token in tokens:
                cleaned_tokens.append(token.get_cleaned())
                single_tagged_tokens.append(token.get_single_tagged())

            article.save_as(' '.join(cleaned_tokens), ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged_tokens), ArtifactType.single_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """

        pattern = re.compile(r'(-\n)|(\d+\s+[^\n]([А-Я]\.)+\s[А-Яа-я]+\s\n)'
                                               r'|(([А-ЯёЁ]([А-Яа-яёЁ\-]+\s)+)\s+\d\s\n)')
        cleaned_text = pattern.sub('', raw_text)
        analyzed_text = Mystem().analyze(cleaned_text)
        tokens = []
        for token in analyzed_text:
            if 'analysis' not in token:
                continue
            if not token['analysis']:
                continue
            morph_token = MorphologicalToken(token['text'])
            morph_token.normalized_form = token['analysis'][0]['lex']
            morph_token.tags_mystem = token['analysis'][0]['gr']
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

    for file in list(path_to_validate.glob('*_raw.txt')):
        with open(file, 'r', encoding='utf-8') as file_text:
            text = file_text.read()
            if not text:
                raise InconsistentDatasetError

    meta_json_counter = 0
    raw_txt_counter = 0
    for file in sorted(path_to_validate.glob('*'), key=lambda x: int(x.name[:x.name.find('_')])):
        if file.name.endswith('meta.json'):
            meta_json_counter += 1
            if f'{meta_json_counter}_meta' not in file.name:
                raise InconsistentDatasetError

        if file.name.endswith('raw.txt'):
            raw_txt_counter += 1
            if f'{raw_txt_counter}_raw' not in file.name:
                raise InconsistentDatasetError

    if not list(path_to_validate.glob('*')):
        raise EmptyDirectoryError

    if meta_json_counter != raw_txt_counter:
        raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
