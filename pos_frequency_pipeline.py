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
        for article in self.corpus_manager.get_articles().values():
            pos_frequency = {}
            with open(article.get_file_path(ArtifactType.single_tagged), 'r', encoding='utf-8') as file:
                text = file.read()
            if not text:
                raise EmptyFileError
            pattern = re.compile(r'<([A-Z]+)')
            tags_found = pattern.findall(text)
            for tag in tags_found:
                if tag not in pos_frequency:
                    pos_frequency[tag] = 1
                else:
                    pos_frequency[tag] += 1
            meta_path = ASSETS_PATH / article.get_meta_file_path()
            with open(meta_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            data.update({'pos_frequencies': pos_frequency})
            with open(meta_path, 'w', encoding='utf-8') as meta_file:
                json.dump(data,
                          meta_file,
                          sort_keys=False,
                          indent=4,
                          ensure_ascii=False,
                          separators=(',', ': '))
            visualize(statistics=pos_frequency, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()


if __name__ == "__main__":
    main()
