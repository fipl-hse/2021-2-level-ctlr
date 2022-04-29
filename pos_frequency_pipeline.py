"""
Implementation of POSFrequencyPipeline for score ten only.
"""

import json
import re

from pipeline import CorpusManager
from constants import ASSETS_PATH
from core_utils.visualizer import visualize


class EmptyFileError(Exception):
    """
    Custom error
    """


class POSFrequencyPipeline:
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager

    def run(self):
        for article_item in self.corpus_manager.get_articles().values():
            article_tag_path = article_item.get_file_path('single_tagged')
            frequencies_dict = {}
            pos_pattern = re.compile(r'<[A-Z]{1,6}')
            #anima_pattern = re.compile(r'не?од=')
            with open(article_tag_path, 'r', encoding='utf-8') as text:
                text_n_tags = text.read()
                if not text_n_tags:
                    raise EmptyFileError
            pos_all = pos_pattern.findall(text_n_tags)
            anima = text_n_tags.count(',од=')
            unanima = text_n_tags.count(',неод=')
            animated_n_count = {'animated': anima, 'unanimated': unanima}
            for pos in pos_all:
                pos_cleaned = pos[1:]
                if pos_cleaned not in frequencies_dict:
                    frequencies_dict[pos_cleaned] = 1
                else:
                    frequencies_dict[pos_cleaned] += 1
            with open(article_item.get_meta_file_path(), "r", encoding='utf-8') as meta_file:
                meta_data = json.load(meta_file)
                if not meta_data:
                    raise EmptyFileError
            meta_data['pos_frequencies'] = frequencies_dict
            with open(article_item.get_meta_file_path(), 'w', encoding='utf-8') as file:
                json.dump(meta_data, file, sort_keys=False,
                          indent=4, ensure_ascii=False, separators=(',', ': '))
            visualize(statistics=frequencies_dict,
                      path_to_save=ASSETS_PATH / f'{article_item.article_id}_image.png')
            visualize(statistics=animated_n_count,
                      path_to_save=ASSETS_PATH / f'{article_item.article_id}_animation_image.png')


def main():
    # YOUR CODE HERE
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
