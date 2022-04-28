"""
Implementation of POSFrequencyPipeline for score ten only.
"""

from collections import Counter
import re

from constants import ASSETS_PATH
from core_utils.visualizer import visualize
from core_utils.article import ArtifactType
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
            tagged_text = article.get_file(ArtifactType.single_tagged)
            pos = re.findall(r"(?<=<)[A-Z]*(?=[,=])", tagged_text)
            meta = article._get_meta() | {"pos_frequencies": dict(Counter(pos))}
            article.save_custom_meta(meta)


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
