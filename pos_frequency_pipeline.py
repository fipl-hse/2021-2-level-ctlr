"""
Implementation of POSFrequencyPipeline for score ten only.
"""

import json
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
            frequencies_dict = {'ADV': 0, 'ADVPRO': 0, 'APRO': 0, 'COM': 0, 'CONJ': 0, 'INTJ': 0, 'NUM': 0,
                        'PART': 0, 'PR': 0, 'S': 0, 'SPRO': 0, 'V': 0}
            with open(article_tag_path, 'r', encoding='utf-8') as text:
                text_n_tags = text.read()
                for pos in frequencies_dict.keys():
                    frequencies_dict[pos] = text_n_tags.count(pos)
            visualize(statistics=frequencies_dict,
                      path_to_save=ASSETS_PATH / f'{article_item.article_id}_image.png')
            with open(article_item.get_meta_file_path(), "r", encoding='utf-8') as meta_file:
                meta_data = json.load(meta_file)
                if not meta_data:
                    raise EmptyFileError
            meta_data['pos_frequencies'] = frequencies_dict
            with open(article_item.get_meta_file_path(), 'w', encoding='utf-8') as file:
                json.dump(meta_data, file, sort_keys=False,
                          indent=4, ensure_ascii=False, separators=(',', ': '))




def main():
    # YOUR CODE HERE
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
