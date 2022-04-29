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
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager

    def run(self):
        articles = self.corpus_manager.get_articles().values()

        for article in articles:
            pos_freq_dict = self._calculate_frequencies(article)

            self._write_to_meta(article, pos_freq_dict)

            visualize(statistics=pos_freq_dict, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')

    def _calculate_frequencies(self, article):
        article_path = article.get_file_path(ArtifactType.single_tagged)

        with open(article_path, 'r', encoding='utf-8') as file:
            text = file.read()

            if not text:
                raise EmptyFileError

        pos_freq_dict = {}
        pos_pattern = re.compile(r'<([A-Z]+)')

        for pos_match in pos_pattern.findall(text):
            pos_freq_dict[pos_match] = pos_freq_dict.get(pos_match, 0) + 1

        return pos_freq_dict

    def _write_to_meta(self, article, pos_freq_dict):
        with open(ASSETS_PATH / article.get_meta_file_path(), 'r', encoding='utf-8') as meta:
            meta_file = json.load(meta)

        meta_file.update({'pos_frequencies': pos_freq_dict})

        with open(ASSETS_PATH / article.get_meta_file_path(), 'w', encoding='utf-8') as meta:
            json.dump(meta_file, meta, ensure_ascii=False, indent=4, separators=(',', ':'))


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
