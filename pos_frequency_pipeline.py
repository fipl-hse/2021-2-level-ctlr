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
            print(article.article_id)
            tagged_text = get_file(article, ArtifactType.single_tagged)
            if not tagged_text:
                raise EmptyFileError

            pos = re.findall(r"(?<=<)[A-Z]*(?=[,=])", tagged_text)
            pos_frequencies = dict(Counter(pos))
            save_updated_meta(article, {"pos_frequencies": pos_frequencies})
            visualize(statistics=pos_frequencies, path_to_save=get_image_path(article))


def get_file(article, kind=ArtifactType):
    with open(article.get_file_path(kind=kind), encoding="utf-8") as file:
        return file.read()


def save_updated_meta(article, update_dict):
    updated_meta = article._get_meta() | update_dict
    with (ASSETS_PATH / article.get_meta_file_path()).open("w", encoding="utf-8") as file:
        json.dump(updated_meta, file, sort_keys=False,
                  indent=4, ensure_ascii=False, separators=(",", ": "))


def get_image_path(article):
    return ASSETS_PATH / f"{article.article_id}_image.png"


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
