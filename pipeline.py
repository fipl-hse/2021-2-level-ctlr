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
        self.path_to_raw_txt_data = Path(path_to_raw_txt_data)
        self._scan_dataset()

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        pattern = re.compile(r'\d+')
        for texts in self.path_to_raw_txt_data.glob("*_raw.txt"):
            if re.match(pattern, texts.name):
                article_id = int(pattern.search(texts.name).group(0))
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
        for article in self.corpus_manager.get_articles().values():
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
        normal_text = raw_text.replace("\n", " ")

        analyzed_text = Mystem().analyze(normal_text)
        morphs = pymorphy2.MorphAnalyzer()

        tokens = []
        for token in analyzed_text:
            if not (token.keys() & {"analysis", "text"} or
                    token.get("analysis") or token.get("text")):
                continue
            if not (token.get("analysis")[0].keys() & {"lex", "gr"} or
                    token.get("analysis")[0].get("lex") or
                    token.get("analysis")[0].get("gr")):
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

    pattern = re.compile(r'\d+')
    raw_texts = sorted(list(path_to_validate.glob('*_raw.txt')), key=lambda x: int(pattern.search(x.name).group(0)))
    metas = sorted(list(path_to_validate.glob('*_meta.json')), key=lambda x: int(pattern.search(x.name).group(0)))

    for text_index, text in enumerate(raw_texts):
        if text.stat().st_size == 0:
            raise InconsistentDatasetError
        file_id = int(pattern.search(text.name).group(0))
        if file_id - text_index != 1 or not (path_to_validate / f'{file_id}_meta.json').is_file():
            raise InconsistentDatasetError

    if len(raw_texts) != len(metas):
        raise InconsistentDatasetError


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
