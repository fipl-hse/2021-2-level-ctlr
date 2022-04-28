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

    def run(self):
        articles = self.corpus_manager.get_articles()
        for article in articles.values():
            path_to_article = article.get_file_path(ArtifactType.single_tagged)

            with open(Path(path_to_article), "r", encoding='utf-8') as file:
                tags = file.read()
                if not tags:
                    raise EmptyFileError

            pos_freq = {}
            pattern = re.compile(r'<([A-Z])+')
            for pos in pattern.findall(tags):
                if pos not in pos_freq:
                    pos_freq[pos] = 0
                else:
                    pos_freq[pos] = pos_freq.get(pos) + 1

            with open(Path(article.get_meta_file_path()), 'a', encoding='utf-8') as meta_file:
                meta_file.write("\n")
                json.dump(pos_freq, meta_file)

            visualize(pos_freq, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    # YOUR CODE HERE
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
