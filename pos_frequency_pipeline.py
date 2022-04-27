"""
Implementation of POSFrequencyPipeline for score ten only.
"""

import json
import re

from constants import ASSETS_PATH
from core_utils.visualizer import visualize
from pipeline import CorpusManager, validate_dataset

class EmptyFileError(Exception):
    """
    Custom error
    """

class POSFrequencyPipeline:
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager

    def run(self):
        for article in self.corpus_manager.get_articles().values():
            frequencies = {}
            pattern = re.compile(r'<([A-Z]+)')
            with open(article.get_file_path('single_tagged'), 'r') as file:
                text = file.read()
                if not text:
                    raise EmptyFileError

            pos_s = pattern.findall(text)
            for pos in pos_s:
                if pos not in frequencies:
                    frequencies[pos] = 1
                else:
                    frequencies[pos] += 1

            with open(article.get_meta_file_path(), 'r') as meta_f:
                json_f = json.load(meta_f)
                if not json_f:
                    raise EmptyFileError

            json_f['pos_frequencies'] = frequencies

            with open(article.get_meta_file_path(), 'w') as file:
                json.dump(json_f, file, sort_keys=False,
                          indent=4, ensure_ascii=False, separators=(',', ': '))

            visualize(statistics=frequencies,
                      path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
