"""
Pipeline for text processing implementation
"""
from pathlib import Path
import re

import pymorphy2
from pymystem3 import Mystem

from constants import ASSETS_PATH, RAW_FILE_PATH_ENDING
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
        pathlib_path_to_data = Path(self.path_to_raw_txt_data)

        for file_path in pathlib_path_to_data.iterdir():
            file_name = file_path.name

            if file_name[-8:] == RAW_FILE_PATH_ENDING:
                match = re.search(r'\d+', file_name)
                article_id = int(match.group(0))

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
            processed_tokens = self._process(raw_text)

            cleaned_tokens = []
            single_tagged_tokens = []
            multiple_tagged_tokens = []

            for processed_token in processed_tokens:
                cleaned_tokens.append(processed_token.get_cleaned())
                single_tagged_tokens.append(processed_token.get_single_tagged())
                multiple_tagged_tokens.append(processed_token.get_multiple_tagged())

            article.save_as(' '.join(cleaned_tokens), ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged_tokens), ArtifactType.single_tagged)
            article.save_as(' '.join(multiple_tagged_tokens), ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        # Gets rid of '-\n's that break up words, so we won't get 'кот-' 'орый' as example (Should be: 'который')
        text = raw_text.replace('-\n', '')

        result = Mystem().analyze(text)

        morphological_tokens = []

        morph = pymorphy2.MorphAnalyzer()

        for token_info in result:
            original_word = token_info['text']

            if not re.match(r'[а-яА-Яa-zA-Z]', original_word):
                continue

            morphological_token = MorphologicalToken(original_word=original_word)

            if 'analysis' not in token_info:
                continue

            if not token_info['analysis']:
                continue

            if not {'lex', 'gr'}.issubset(set(token_info['analysis'][0])):
                continue

            morphological_token.normalized_form = token_info['analysis'][0]['lex']
            morphological_token.tags_mystem = token_info['analysis'][0]['gr']

            parsed_word = morph.parse(original_word)[0]
            morphological_token.tags_pymorphy = parsed_word.tag

            morphological_tokens.append(morphological_token)

        return morphological_tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """

    pathlib_path_to_validate = Path(path_to_validate)

    if not path_to_validate.exists():
        raise FileNotFoundError

    if not pathlib_path_to_validate.is_dir():
        raise NotADirectoryError

    file_ids = []

    for file_path in pathlib_path_to_validate.iterdir():
        file_name = file_path.name

        # In case this annoying macOS Finder system file exists locally
        if file_name == '.DS_Store':
            file_path.unlink()
            continue

        match = re.match(r'\d+', file_name)

        if not match:
            raise InconsistentDatasetError

        file_id = int(match.group(0))

        file_ids.append(file_id)

    file_ids = sorted(file_ids)

    last_file_id = 0

    for file_id in file_ids:
        if not last_file_id and file_id != 1 or file_id - last_file_id > 1:
            raise InconsistentDatasetError

        last_file_id = file_id

    if not last_file_id:
        raise EmptyDirectoryError


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
