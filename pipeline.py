"""
Pipeline for text processing implementation
"""
import re
from pathlib import Path
from core_utils.article import Article, ArtifactType
# from pymystem3 import Mystem


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
        pass

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

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        dataset = list(self.path.glob('*'))
        pattern = re.compile(r'([0-9]+)_raw')

        for file in dataset:
            if 'raw.txt' in file.name:
                article_id = pattern.search(file.name).group(1)
                self._storage[int(article_id)] = Article(url=None, article_id=int(article_id))

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
        articles = self.corpus_manager.get_articles().values()
        for article in articles:
            raw_text = article.get_raw_text()
            processed_text = self._process(raw_text)

            cleaned_tokens = []
            for token in processed_text:
                cleaned_tokens.append(token.get_cleaned())

            article.save_as(' '.join(cleaned_tokens), ArtifactType.cleaned)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        clean_text = ''
        for symbol in raw_text:
            if symbol.isalpha():
                clean_text += symbol
            if symbol.isspace() or symbol == '\n':
                clean_text += ' '
            if symbol == '-\n':
                clean_text += ''
        clean_list = clean_text.split()

        morph_tokens = []
        for word in clean_list:
            token = MorphologicalToken(original_word=word)
            morph_tokens.append(token)

        return morph_tokens


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

    dataset = list(path_to_validate.glob('*'))
    if not dataset:
        raise EmptyDirectoryError

    for file in dataset:
        if 'raw.txt' in file.name:
            with open(file, 'r', encoding='utf-8') as text_file:
                text = text_file.read()
                if not text:
                    raise InconsistentDatasetError

    counter_t = 0
    counter_m = 0
    for file in dataset:
        if 'meta' in file.name:
            counter_m += 1
        elif 'raw.txt' in file.name:
            counter_t += 1

    if counter_t != counter_m:
        raise InconsistentDatasetError


def main():
    pass


if __name__ == "__main__":
    main()
