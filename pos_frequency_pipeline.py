"""
Implementation of POSFrequencyPipeline for score ten only.
"""

import json
import re
from pathlib import Path

from constants import ASSETS_PATH
from core_utils.visualizer import visualize
from pipeline import CorpusManager, validate_dataset


class EmptyFileError(Exception):
    """
    Custom error
    """


class POSFrequencyPipeline:
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager
        self.frequencies = {}

    def run(self):
        for idx, article in self.corpus_manager.get_articles().items():
            processed_text_path = article.get_file_path(kind="single_tagged")
            with open(processed_text_path, encoding="utf-8") as file:
                text = file.read()

            if not text:
                raise EmptyFileError

            self.frequencies = self._calculate_frequencies(text)
            self._update_meta(idx)

            visualize(
                statistics=self.frequencies,
                path_to_save=Path(ASSETS_PATH) / f"{idx}_image.png"
            )

    def _calculate_frequencies(self, processed_text):
        pos = re.findall(r"(?<=<)[A-Z]+|(?<=\()[A-Z]+", processed_text)
        pos_freq = {}
        for tag in pos:
            if tag in pos_freq:
                pos_freq[tag] += 1
            else:
                pos_freq[tag] = 1
        return pos_freq

    def _update_meta(self, meta_id):
        path = Path(ASSETS_PATH) / f"{meta_id}_meta.json"

        with open(path, encoding="utf-8") as file:
            article_meta = json.load(file)
            article_meta["pos_frequencies"] = self.frequencies

        with open(path, "w", encoding="utf-8") as file:
            json.dump(article_meta, file)


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
