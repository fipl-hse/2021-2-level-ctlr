"""
Pipeline for text processing implementation
"""
import re
from pathlib import Path
from pymystem3 import Mystem
import pymorphy2
from core_utils.article import Article, ArtifactType
from constants import ASSETS_PATH

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
        path_to_data = Path(self.path_to_raw_txt_data)
        for file in path_to_data.glob('*.txt'):
            article_id = int(file.stem.split('_')[0])
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
            tokens = self._process(article.get_raw_text())

            articles_tokens = []
            single_tagged = []
            multiple_tagged = []

            for token in tokens:
                articles_tokens.append(token.get_cleaned())
                single_tagged.append(token.get_single_tagged())
                multiple_tagged.append(token.get_multiple_tagged())

            article.save_as(' '.join(articles_tokens), ArtifactType.cleaned)
            article.save_as(' '.join(single_tagged), ArtifactType.single_tagged)
            article.save_as(' '.join(multiple_tagged), ArtifactType.multiple_tagged)

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        cleaned_text = ' '.join(re.findall(r'[а-яёА-ЯЁ]+', raw_text))
        analyzed_text = Mystem().analyze(cleaned_text)
        morph_analyzing = pymorphy2.MorphAnalyzer()

        tokens = []
        for token in analyzed_text:

            if 'analysis' not in token:
                continue
            if not token['analysis']:
                continue

            morph_tokens = MorphologicalToken(token['text'])
            morph_tokens.normalized_form = token['analysis'][0].get('lex')
            morph_tokens.tags_mystem = token['analysis'][0].get('gr')
            tokens.append(morph_tokens)
            morph_tokens.tags_pymorphy = morph_analyzing.parse(token['text'])[0].tag
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

    raw_txt_files = list(path.glob('*raw.txt'))
    meta_files = list(path.glob('*meta.json'))
    all_files = meta_files + raw_txt_files
    if not all_files:
        raise EmptyDirectoryError
    if len(raw_txt_files) != len(meta_files):
        raise InconsistentDatasetError

    data = list(path.glob('*.txt'))

    articles_ids = []

    for file in data:
        with open(file, 'r', encoding='utf-8') as text_file:
            text = text_file.read()
        if not text:
            raise InconsistentDatasetError

        pattern = re.match(r'\d+', file.name)
        if not pattern:
            raise InconsistentDatasetError

        article_id = int(pattern.group(0))
        articles_ids.append(article_id)

    if not articles_ids:
        raise EmptyDirectoryError

    previous_article_id = 0
    sorted_all_ids = sorted(articles_ids)
    if sorted_all_ids[0] != 1:
        raise InconsistentDatasetError
    for article_id in sorted_all_ids:
        if article_id - previous_article_id > 1:
            raise InconsistentDatasetError
        previous_article_id = article_id




def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = TextProcessingPipeline(corpus_manager)
    pipeline.run()

if __name__ == "__main__":
    main()
