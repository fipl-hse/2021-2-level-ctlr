"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import json
import re

from constants import ASSETS_PATH
from core_utils.article import ArtifactType
from core_utils.visualizer import visualize
from pipeline import CorpusManager, validate_dataset


class EmptyFileError(Exception):
    """
    Custom error
    """


class POSFrequencyPipeline:
    def __init__(self, corpus_manager):
        self.corpus_manager = corpus_manager

    def run(self):
        articles = self.corpus_manager.get_articles().values()

        for article in articles:
            pos_frequencies = self.calculate_pos_frequencies(article)

            self.save_pos_frequencies(article, pos_frequencies)
            visualize(statistics=pos_frequencies, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')

    def calculate_pos_frequencies(self, article):
        """
        Calculates POS frequencies for one article
        """
        pos_frequencies = {}

        article_path = article.get_file_path(ArtifactType.single_tagged)

        with open(article_path, 'r', encoding='utf-8') as text_file:
            text = text_file.read()

        if not text:
            raise EmptyFileError

        prog = re.compile(r'<(?P<pos_tag>[A-Z]+)')
        res = prog.finditer(text)

        for match in res:
            pos_frequencies[match.group('pos_tag')] = pos_frequencies.get(match.group('pos_tag'), 0) + 1

        return pos_frequencies

    def save_pos_frequencies(self, article, pos_frequencies):
        with open(ASSETS_PATH / article.get_meta_file_path(), 'r', encoding='utf-8') as meta_file:
            meta_data = json.load(meta_file)

        meta_data.update({'pos_frequencies': pos_frequencies})

        with open(ASSETS_PATH / article.get_meta_file_path(), 'w', encoding='utf-8') as meta_file:
            json.dump(meta_data, meta_file, sort_keys=False,
                      indent=4, ensure_ascii=False, separators=(',', ': '))


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
