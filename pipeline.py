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
        self.path_to_raw_txt_data = Path(path_to_raw_txt_data)
        self._storage = {}
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        visited_ids = []
        compiled_expression = re.compile(r'\d+')
        for file in self.path_to_raw_txt_data.iterdir():
            pattern = compiled_expression.search(file.name)
            if not pattern:
                continue
            article_id = int(pattern.group(0))
            if article_id in visited_ids:
                continue
            article = Article(url=None, article_id=article_id)
            visited_ids.append(article_id)
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
        pass

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
            multiple_tagged_tokens = []
            for token in tokens:
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
        cleaned_text = raw_text.replace('-\n', '')
        analyzed_cleaned_text = Mystem().analyze(cleaned_text)
        morph = pymorphy2.MorphAnalyzer()
        tokens = []
        for token in analyzed_cleaned_text:
            if not token.get('analysis') or not token.get('text'):
                continue
            if not isinstance(token['analysis'], list) or not isinstance(token['analysis'][0], dict):
                continue
            if 'lex' not in token['analysis'][0] or 'gr' not in token['analysis'][0]:
                continue
            morphological_token = MorphologicalToken(original_word=token['text'])
            morphological_token.normalized_form = token['analysis'][0]['lex']
            morphological_token.tags_mystem = token['analysis'][0]['gr']
            parsed_word = morph.parse(token['text'])
            if not parsed_word:
                continue
            morphological_token.tags_pymorphy = parsed_word[0].tag
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
    all_ids = []
    compiled_expression = re.compile(r'(\d+)_(?:raw.txt|meta.json|raw.pdf'
                                     r'|cleaned.txt|single_tagged.txt'
                                     r'|multiple_tagged.txt)')
    for file in path.iterdir():
        if file.stat().st_size == 0:
            raise InconsistentDatasetError("File is empty")
        full_pattern = compiled_expression.match(file.name)
        if not full_pattern:
            raise InconsistentDatasetError("Incorrect file name")
        article_id = int(full_pattern.group(1))
        if article_id < 1:
            raise InconsistentDatasetError("Article ids do not start from 1")
        all_ids.append(article_id)
    if not all_ids:
        raise EmptyDirectoryError
    previous_article_id = 0
    sorted_all_ids = sorted(all_ids)
    for article_id in sorted_all_ids:
        if article_id - previous_article_id > 1:
            raise InconsistentDatasetError("Article ids are not consistent")
        previous_article_id = article_id
    if sorted_all_ids[0] != 1:
        raise InconsistentDatasetError("Article ids do not start from 1")
    for number in set(sorted_all_ids):
        name_for_raw = f'{number}_raw.txt'
        name_for_meta = f'{number}_meta.json'
        raw_path = path / name_for_raw
        meta_path = path / name_for_meta
        if not raw_path.exists() or not meta_path.exists():
            raise InconsistentDatasetError(f"There are no meta or raw files for an article ID: {number}")




def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()
    # YOUR CODE HERE


if __name__ == "__main__":
    main()
