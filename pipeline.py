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
        article_id = 0

        while True:
            article = Article(url=None, article_id=article_id)

            # article_id > 0 is meant to solve CI where files may start from 0 during CorpusManager init
            if not article.get_raw_text_path().exists() and article_id > 0:
                break

            if not article.get_raw_text_path().exists() and article_id == 0:
                continue

            self._storage[article_id] = article
            article_id += 1

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

            if not token_info.get('analysis'):
                continue

            if 'lex' not in token_info['analysis'][0] or 'gr' not in token_info['analysis'][0]:
                continue

            morphological_token = MorphologicalToken(original_word=original_word)

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

    if not pathlib_path_to_validate.exists():
        raise FileNotFoundError

    if not pathlib_path_to_validate.is_dir():
        raise NotADirectoryError

    file_ids = []

    for file_path in pathlib_path_to_validate.iterdir():
        match = re.match(r'\d+', file_path.name)

        if not match:
            raise InconsistentDatasetError("Found a file name that does not correspond to the naming scheme")

        if file_path.stat().st_size == 0:
            raise InconsistentDatasetError("File is empty")

        file_id = int(match.group(0))

        if file_id not in file_ids:
            file_ids.append(file_id)

    if not file_ids:
        raise EmptyDirectoryError("The assets directory is empty")

    file_ids = sorted(file_ids)

    last_file_id = 0

    for file_id in file_ids:
        if not last_file_id and file_id != 1:
            raise InconsistentDatasetError("Files do not start from 1")

        if file_id - last_file_id > 1:
            raise InconsistentDatasetError("Files are inconsistent")

        if not (pathlib_path_to_validate / f'{file_id}_raw.txt').is_file() or \
                not (pathlib_path_to_validate / f'{file_id}_meta.json').is_file():
            raise InconsistentDatasetError(f"There are no meta or raw files for an article ID: {file_id}")

        last_file_id = file_id


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
