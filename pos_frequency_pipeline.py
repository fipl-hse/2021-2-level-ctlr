"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import json
import re

from constants import ASSETS_PATH
from core_utils.visualizer import visualize
from pipeline import CorpusManager


class EmptyFileError(Exception):
    """
    Custom error
    """


class POSFrequencyPipeline:
    def __init__(self, corpus_manager):
        self.corpus_manager = corpus_manager

    def run(self):
        for article in self.corpus_manager.get_articles().values():
            pos_frequencies = {}

            article_path = article.get_file_path('single_tagged')

            with open(article_path, 'r') as text_file:
                text = text_file.read()

                if not text:
                    raise EmptyFileError

                tokens = text.split()

                for token in tokens:
                    match = re.search(r'<[A-Z]+', token)

                    if not match:
                        continue

                    pos = match.group(0)[1:]
                    pos_frequencies[pos] = pos_frequencies.get(pos, 0) + 1

            with open(ASSETS_PATH / article.get_meta_file_path(), 'r', encoding='utf-8') as meta_file:
                meta_data = json.load(meta_file)
                meta_data.update({'pos_frequencies': pos_frequencies})

            with open(ASSETS_PATH / article.get_meta_file_path(), 'w', encoding='utf-8') as meta_file:
                json.dump(meta_data, meta_file, sort_keys=False,
                          indent=4, ensure_ascii=False, separators=(',', ': '))

            visualize(statistics=pos_frequencies, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    corpus_manager = CorpusManager(ASSETS_PATH)

    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
