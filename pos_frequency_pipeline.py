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
            article_path = article.get_file_path(ArtifactType.single_tagged)

            with open(article_path, encoding='utf-8') as file:
                text = file.read()
                if not text:
                    raise EmptyFileError

            pattern = re.compile(r'<([A-Z]+)')
            all_pos = pattern.findall(text)
            frequencies_dict = {}

            for pos in all_pos:
                frequencies_dict[pos] = all_pos.count(pos)

            meta_path = article.get_meta_file_path()
            with open(ASSETS_PATH / meta_path, encoding='utf-8') as file:
                meta_data = json.load(file)

            meta_data.update({'pos_frequencies': frequencies_dict})

            with open(ASSETS_PATH / meta_path, 'w', encoding='utf-8') as file:
                json.dump(meta_data, file, ensure_ascii=False, indent=4, separators=(',', ':'))

            visualize(statistics=frequencies_dict, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    # YOUR CODE HERE
    print('some preparations')
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
    pos_pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    print('run pos pipeline...')
    pos_pipeline.run()
    print('now you got images!')


if __name__ == "__main__":
    main()
