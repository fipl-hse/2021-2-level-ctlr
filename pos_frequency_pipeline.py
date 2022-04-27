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
            path_to_article = article.get_file_path(ArtifactType.single_tagged)
            with open(path_to_article, encoding='utf-8') as file:
                text = file.read()
                if not text:
                    raise EmptyFileError

            pattern = re.compile(r'<([A-Z]+)')
            freq_dict = {}
            parts_of_speech = pattern.findall(text)

            for element in parts_of_speech:
                if element not in freq_dict:
                    freq_dict[element] = parts_of_speech.count(element)

            with open(ASSETS_PATH / article.get_meta_file_path(), encoding='utf-8') as meta_file:
                meta_data = json.load(meta_file)

            meta_data.update({'pos_frequencies': freq_dict})

            with open(ASSETS_PATH / article.get_meta_file_path(), 'w', encoding='utf-8') as meta_file:
                json.dump(meta_data, meta_file, ensure_ascii=False, indent=4, separators=(',', ':'))

            visualize(statistics=freq_dict, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    # YOUR CODE HERE
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
