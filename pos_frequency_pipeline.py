"""
Implementation of POSFrequencyPipeline for score ten only.
"""
import json
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
        pass

    def run(self):
        for article in self.corpus_manager.get_articles().values():
            frequency_dict = {}
            with open(article.get_file_path(ArtifactType.single_tagged), 'r', encoding='utf-8') as file:
                text = file.read()
            if not text:
                raise EmptyFileError
            pattern = re.compile(r'<([A-Z]+)')
            all_tags = pattern.findall(text)
            for tag in all_tags:
                if tag not in frequency_dict:
                    frequency_dict[tag] = 1
                else:
                    frequency_dict[tag] += 1
            noun_pattern = re.compile(r'([a-яё]+)<(SPRO|S)')
            all_nouns = noun_pattern.finditer(text)
            longest_noun = ''
            for noun in all_nouns:
                if len(noun.group(1)) > len(longest_noun):
                    longest_noun = noun.group(1)
            print(longest_noun)
            with open(ASSETS_PATH / article.get_meta_file_path(), 'r', encoding='utf-8') as file:
                data = json.load(file)
            data.update({'pos_frequencies': frequency_dict})
            with open(ASSETS_PATH / article.get_meta_file_path(), 'w', encoding='utf-8') as meta_file:
                json.dump(data, meta_file, sort_keys=False,
                          indent=4, ensure_ascii=False, separators=(',', ': '))
            visualize(statistics=frequency_dict, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    # YOUR CODE HERE
    corpus_manager = CorpusManager(ASSETS_PATH)
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    pipeline.run()
    pass


if __name__ == "__main__":
    main()
