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
            with open(article.get_file_path('single_tagged'),
                      'r', encoding='utf-8') as file_single_tagged:
                text_single_tagged = file_single_tagged.read()
            if not text_single_tagged:
                raise EmptyFileError
            pos_frequencies = {}
            pos_dict = re.findall(r'<([A-Z]+)', text_single_tagged)
            if not pos_dict:
                continue
            for pos in pos_dict:
                if pos not in pos_frequencies:
                    pos_frequencies[pos] = 1
                else:
                    pos_frequencies[pos] += 1
            with open(article.get_file_path('multiple_tagged'),
                      'r', encoding='utf-8') as file_multiple_tagged:
                text_multiple_tagged = file_multiple_tagged.read()
            noun_find = re.findall('\(NOUN[a-z,\s]+plur[a-z,\s]+\)', text_multiple_tagged)
            print(len(noun_find))
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
