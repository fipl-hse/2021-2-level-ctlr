"""
POSFrequency Pipeline implementation
"""
import json
import re

from constants import ASSETS_PATH
from core_utils.article import ArtifactType
from core_utils.visualizer import visualize
from pipeline import validate_dataset, CorpusManager


class EmptyFileError(Exception):
    """
    If File is empty
    """


class POSFrequencyPipeline:
    """
    Process articles from corpus manager
    """
    def __init__(self, corpus_manager):
        self.corpus_manager = corpus_manager

    def run(self):
        """
        Runs POSFrequencyPipleine process scenario
        """
        articles = self.corpus_manager.get_articles().values()
        for article in articles:
            freq_pos_dict = self._calculate_pos_freq(article)

            meta_file_path = article.get_meta_file_path()
            with open(meta_file_path, encoding='Utf-8') as meta:
                meta_file = json.load(meta)

            meta_file["pos_frequencies"] = freq_pos_dict
            with meta_file_path.open("w", encoding='utf-8') as file:
                json.dump(meta_file, file, sort_keys=False,
                          indent=4, ensure_ascii=False, separators=(',', ': '))

            visualize(statistics=freq_pos_dict, path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')

    def _calculate_pos_freq(self, article):
        """
        Calculates position frequency
        """
        freq_pos_dict = {}

        path_to_article = article.get_file_path(kind=ArtifactType.single_tagged)

        with open(path_to_article, encoding='Utf-8') as file:
            text = file.read()

        if not text:
            raise EmptyFileError

        pattern_for_tags = re.compile(r'<([a-zA-Z]+)')
        tags = pattern_for_tags.finditer(text)
        for tag in tags:
            name_tag = tag.group(1)
            if name_tag in freq_pos_dict:
                freq_pos_dict[name_tag] += 1
            else:
                freq_pos_dict[name_tag] = 1
        return freq_pos_dict


def main():
    validate_dataset(ASSETS_PATH)
    print('Validating dataset is done!')
    corpus_manager = CorpusManager(ASSETS_PATH)
    print('Corpus manager is created!')
    pipeline = POSFrequencyPipeline(corpus_manager=corpus_manager)
    print('POSFrequencyPipeline is created!')
    pipeline.run()
    print('Done!')


if __name__ == '__main__':
    main()
