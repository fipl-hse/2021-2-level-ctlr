"""
Pipeline for text processing implementation
"""
import re
from pathlib import Path
# from pymystem3 import Mystem
from core_utils.article import Article, ArtifactType
from constants import ASSETS_PATH
# check


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
        pattern = re.compile(r'[0-9]+')

        for file in dataset:
            if 'raw.txt' in file.name:
                article_id = int(pattern.search(file.name).group(0))
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
        text = raw_text.replace('-\n', '')
        clean_text = ''
        pattern = re.compile(r'[а-яА-Яa-zA-Z]')

        for symbol in text:
            if pattern.match(symbol):
                clean_text += symbol
            if symbol.isspace() or symbol == '\n':
                clean_text += ' '

        clean_list = clean_text.split()

        morph_tokens = []
        for word in clean_list:
            token = MorphologicalToken(original_word=word)
            morph_tokens.append(token)

        return morph_tokens

        # result = Mystem().analyze(raw_text)
        # morph_tokens = []

        # for element in result:
        # word = element['text']
        # if not word.isalpha():
        # continue

        # token = MorphologicalToken(original_word=word)
        # morph_tokens.append(token)


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

    pattern = re.compile(r'[0-9]+')
    sorted_dataset = sorted(dataset, key=lambda x: int(pattern.search(x.name).group(0)))

    true_id = 0
    for file in sorted_dataset:
        file_id = int(pattern.search(file.name).group(0))
        if file_id == 0 or file_id - true_id > 1 or \
                not (path_to_validate / f'{file_id}_raw.txt').is_file() or \
                not (path_to_validate / f'{file_id}_meta.json').is_file():
            raise InconsistentDatasetError
        true_id = file_id


def main():
    print('some preparations')
    validate_dataset(ASSETS_PATH)
    print('implementing corpus manager')
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    print('run pipeline...')
    pipeline.run()


if __name__ == "__main__":
    main()
