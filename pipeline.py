"""
Pipeline for text processing implementation
"""
import re

from pathlib import Path
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer

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
        path_to_raw_txt_data = Path(self.path_to_raw_txt_data)
        pattern = re.compile(r'\d+')
        for file in path_to_raw_txt_data.glob("*.txt"):
            file_match = re.search(pattern, file.name)
            if not file_match:
                continue
            article_id = int(file_match.group(0))
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
            multiple_tagged_tokens = []
            for token in tokens:
                cleaned_tokens.append(token.get_cleaned())
                single_tagged_tokens.append(token.get_single_tagged())
                multiple_tagged_tokens.append(token.get_multiple_tagged())
            article.save_as(" ".join(cleaned_tokens), kind=ArtifactType.cleaned)
            article.save_as(" ".join(single_tagged_tokens), kind=ArtifactType.single_tagged)
            article.save_as(" ".join(multiple_tagged_tokens), kind=ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        processed_text = Mystem().analyze(raw_text)
        tokens = []
        pymorph_analyzer = MorphAnalyzer()
        for processed_word in processed_text:
            if not processed_word.get('text') or not processed_word.get('analysis'):
                continue
            morph_token = MorphologicalToken(original_word=processed_word['text'])
            morph_token.normalized_form = processed_word['analysis'][0]['lex']
            morph_token.tags_mystem = processed_word['analysis'][0]['gr']
            morph_token.tags_pymorphy = pymorph_analyzer.parse(processed_word['text'])[0].tag
            tokens.append(morph_token)
        return tokens


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    path_to_validate = Path(path_to_validate)

    if not path_to_validate.exists():
        raise FileNotFoundError('Path not exits')

    if not path_to_validate.is_dir():
        raise NotADirectoryError('Path is not a directory')

    counter_txt = 0
    for file in path_to_validate.glob('*'):
        if file.stat().st_size == 0:
            raise InconsistentDatasetError(f'{file.name} is empty')
        if file.name.endswith('raw.txt'):
            counter_txt += 1
            path_for_meta = path_to_validate / f'{counter_txt}_meta.txt'
            path_for_txt = path_to_validate / f'{counter_txt}_raw.txt'
            if not path_for_txt or not path_for_meta:
                raise InconsistentDatasetError

    pattern_for_filename = re.compile(r'(\d+)_(cleaned.txt|meta.json|multiple_tagged.txt|raw.txt|raw.pdf'
                                      r'|single_tagged.txt)')
    all_ids = []
    for file in path_to_validate.glob('*'):
        match_for_name = pattern_for_filename.match(file.name)
        if not match_for_name:
            raise InconsistentDatasetError('Incorrect file name')
        all_ids.append(int(match_for_name.group(1)))
    if not all_ids:
        raise EmptyDirectoryError('Directory is empty!')

    sorted_all_ids = sorted(all_ids)
    previous_id_of_file = 0
    for id_of_file in sorted_all_ids:
        if id_of_file - previous_id_of_file > 1:
            raise InconsistentDatasetError('Dataset is inconsistent')
        previous_id_of_file = id_of_file

    if sorted_all_ids[0] != 1:
        raise InconsistentDatasetError()

    counter_txt = 0
    counter_meta = 0
    for file in path_to_validate.glob('*'):
        if file.name.endswith('raw.txt'):
            counter_txt += 1
        elif file.name.endswith('meta.json'):
            counter_meta += 1
    if counter_txt != counter_meta:
        raise InconsistentDatasetError('Dataset is imbalanced')


def main():
    validate_dataset(ASSETS_PATH)
    print('Validating dataset is done!')
    corpus_manager = CorpusManager(ASSETS_PATH)
    print('Corpus manager is created!')
    pipeline = TextProcessingPipeline(corpus_manager=corpus_manager)
    print('Pipeline is created!')
    pipeline.run()
    print('Done!')


if __name__ == "__main__":
    main()
