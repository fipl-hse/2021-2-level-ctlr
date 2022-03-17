"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import re

import json
from pathlib import Path

from core_utils.article import ArtifactType
from core_utils.visualizer import visualize
from pipeline import CorpusManager

from constants import ASSETS_PATH


class EmptyFileError(Exception):
    """
    No data to process: empty article file
    """


class POSFrequencyPipeline:
    """
    Counts frequencies of each POS in articles,
    updates meta information and produces graphic report
    """
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus = corpus_manager

    def run(self):
        articles = self.corpus.get_articles()
        for article in articles.values():
            frequencies = self._count_frequencies(article)
            if not frequencies:
                raise EmptyFileError
            self._update_meta(article, frequencies)
            visualize(frequencies, str(Path(ASSETS_PATH) / f'{article.article_id}_image.png'))

    def _count_frequencies(self, article):
        with open(article.get_file_path(ArtifactType.multiple_tagged), encoding='utf-8') as file:
            contents = file.read()
        tags_found = re.findall(r"<([A-Z]+)[,=]?", contents)
        frequencies = {}
        for tag in tags_found:
            frequencies[tag] = tags_found.count(tag)
        return frequencies

    def _update_meta(self, article, frequencies):
        with open(article.get_meta_file_path(), 'r', encoding='utf-8') as meta_file:
            meta = json.load(meta_file)
        meta['pos_frequencies'] = frequencies
        with open(article.get_meta_file_path(), 'w', encoding='utf-8') as meta_file:
            json.dump(meta,
                      meta_file,
                      sort_keys=False,
                      indent=4,
                      ensure_ascii=False,
                      separators=(',', ': '))


def main():
    corpus_manager = CorpusManager(ASSETS_PATH)
    visualizer = POSFrequencyPipeline(corpus_manager)
    visualizer.run()


if __name__ == "__main__":
    main()
