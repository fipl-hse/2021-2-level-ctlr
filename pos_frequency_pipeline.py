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
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager

    def run(self):
        for article in self.corpus_manager.get_articles().values():
            single_tagged_path = article.get_file_path('single_tagged')
            with open(single_tagged_path, 'r', encoding='utf-8') as file:
                text = file.read()
            if not text:
                raise EmptyFileError
            tokens = text.split()
            pos_frequencies = {}
            pos_pattern = re.compile('[A-Z]+')
            for token in tokens:
                pos = pos_pattern.search(token)
                if not pos:
                    continue
                pos = pos.group()
                if pos not in pos_frequencies:
                    pos_frequencies[pos] = 1
                else:
                    pos_frequencies[pos] += 1
            with open(article.get_meta_file_path(), 'r', encoding='utf-8') as meta_file:
                meta_data = json.load(meta_file)
                if not meta_data:
                    raise EmptyFileError
                meta_data.update({'pos_frequencies': pos_frequencies})
            with open(article.get_meta_file_path(), 'w', encoding='utf-8') as meta_file:
                json.dump(meta_data, meta_file, sort_keys=False,
                          indent=4, ensure_ascii=False,
                          separators=(',', ': '))
            visualize(pos_frequencies,
                      ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    # YOUR CODE HERE
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
