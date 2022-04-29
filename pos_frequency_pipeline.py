"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import json
from pathlib import Path
import re

from constants import ASSETS_PATH
from core_utils.article import ArtifactType
from core_utils.visualizer import visualize
from pipeline import CorpusManager


class EmptyFileError(Exception):
    """
    Custom error
    """


class POSFrequencyPipeline:
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager
        self.pos_freq = {}

    def _find_tags(self, article):
        path_to_article = article.get_file_path(ArtifactType.single_tagged)

        with open(Path(path_to_article), "r", encoding='utf-8') as file:
            tags = file.read()
            if not tags:
                raise EmptyFileError
            return tags

    def _pos_counter(self, tags):
        pattern = re.compile(r'<([A-Z]+)')
        for pos in pattern.findall(tags):
            self.pos_freq[pos] = self.pos_freq.get(pos, 0) + 1

    def _update_meta(self, article):
        with open(Path(article.get_meta_file_path()), 'r', encoding='utf-8') as meta_file:
            meta = json.load(meta_file)
        meta.update({"pos_frequencies": self.pos_freq})
        with open(Path(article.get_meta_file_path()), 'w', encoding='utf-8') as new_meta_file:
            json.dump(meta, new_meta_file, sort_keys=False,
                      indent=4, ensure_ascii=False, separators=(',', ': '))

    def run(self):
        for article in self.corpus_manager.get_articles().values():
            self._pos_counter(self._find_tags(article))
            self._update_meta(article)
            visualize(self.pos_freq, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')
            self.pos_freq.clear()


def main():
    # YOUR CODE HERE
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
