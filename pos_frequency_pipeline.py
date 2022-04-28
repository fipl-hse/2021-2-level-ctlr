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
    """
    Parts of speech frequency visualizer
    """
    def __init__(self, corpus_manager: CorpusManager):
        self.corpus_manager = corpus_manager

    def run(self):
        """
        Runs POSFrequencyPipeline
        """
        for article in self.corpus_manager.get_articles().values():
            with open(article.get_file_path(kind=ArtifactType.single_tagged),
                      'r', encoding='utf-8') as single_tagged_file:
                text = single_tagged_file.read()
            if not text:
                raise EmptyFileError(f'NO DATA TO VISUALIZE FOR '
                                     f'{article.article_id}_single_tagged.txt FILE.')

            pos_freq_dict = {}
            pos_tag_pattern = re.compile(r'(?<=<)[A-Z]+')

            for pos_tag in pos_tag_pattern.findall(text):
                pos_freq_dict[pos_tag] = pos_freq_dict.get(pos_tag, 0) + 1

            with open(ASSETS_PATH / article.get_meta_file_path(),
                      'r', encoding='utf-8') as meta_file:
                data = json.load(meta_file)
            if not data:
                raise EmptyFileError(f'NO META INFORMATION FOR '
                                     f'{article.article_id}_meta.json FILE')
            data.update({'pos_frequencies': pos_freq_dict})

            with open(ASSETS_PATH / article.get_meta_file_path(),
                      'w', encoding='utf-8') as meta_file:
                json.dump(data, meta_file, ensure_ascii=False, indent=4, separators=(',', ':'))

            visualize(statistics=pos_freq_dict,
                      path_to_save=ASSETS_PATH / f'{article.article_id}_image.png')


def main():
    print(f'RUNNING VISUALIZER...\nFOUND {len(list(ASSETS_PATH.glob("*_single_tagged.txt")))} '
          f'FILES TO VISUALIZE.\nVALIDATING DATASET...')
    validate_dataset(ASSETS_PATH)
    print('DATASET IS CORRECT.\nCREATING CORPUS MANAGER ABSTRACTION...')
    corpus_manager = CorpusManager(ASSETS_PATH)
    print('DONE.\nCREATING PIPELINE VISUALIZER INSTANCE...')
    pipeline = POSFrequencyPipeline(corpus_manager)
    print('DONE.\nRUNNING POS FREQUENCY VISUALIZER PIPELINE ON COLLECTED FILES...')
    pipeline.run()
    print('DONE.\nPROGRAM FINISHED.')


if __name__ == "__main__":
    main()
