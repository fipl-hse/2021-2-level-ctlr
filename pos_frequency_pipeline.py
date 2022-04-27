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
        """
        Runs pipeline process scenario:
        iterates through the available articles taken from CorpusManager,
        reads each file,
        calculates frequencies of each part of speech,
        writes them to the meta file
        visualizes them in a form of images with names following this convention: N_image.png.
        """

        for article in self.corpus_manager.get_articles().values():

            with open(article.get_file_path(ArtifactType.single_tagged), encoding='utf=8') as file:
                file_text = file.read()
                if not file_text:
                    raise EmptyFileError

            # calculate frequencies of each part of speech
            freq_dict = {}
            pattern = re.compile(r'<([A-Z]+)')

            for pos_tag in pattern.findall(file_text):
                freq_dict[pos_tag] = freq_dict.get(pos_tag, 0) + 1

            # write frequencies to the meta file
            with open(ASSETS_PATH / article.get_meta_file_path(), encoding='utf-8') as meta_f:
                meta_data = json.load(meta_f)

            meta_data.update({'pos_frequencies': freq_dict})

            with open(ASSETS_PATH / article.get_meta_file_path(), 'w', encoding='utf-8') as meta_f:
                json.dump(meta_data, meta_f, sort_keys=False, indent=4,
                          ensure_ascii=False, separators=(',', ':'))

            # visualize frequencies in a form of images with names N_image.png.
            visualize(statistics=freq_dict,
                      path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
