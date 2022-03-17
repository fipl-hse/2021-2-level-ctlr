import json
import os
import unittest

import pytest
import shutil

from constants import ASSETS_PATH, PROJECT_ROOT
from pipeline import CorpusManager, TextProcessingPipeline, validate_dataset
from pos_frequency_pipeline import POSFrequencyPipeline, EmptyFileError
from config.test_params import TEST_FILES_FOLDER


MYSTEM_TAGS = ['A', 'ADV', 'ADVPRO', 'ANUM', 'APRO', 'COM', 'CONJ', 'INTJ', 'NUM', 'PART', 'PR', 'S', 'SPRO', 'V']
TEST_TMP = os.path.join(PROJECT_ROOT, 'tmp_tests')


class PosFrequencyPipelineTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        validate_dataset(ASSETS_PATH)
        shutil.copytree(ASSETS_PATH, TEST_TMP)  # cash ASSETS_PATH state before modifying it for testing
        shutil.copyfile(os.path.join(TEST_FILES_FOLDER, "0_raw.txt"), os.path.join(ASSETS_PATH, "0_raw.txt"))
        shutil.copyfile(os.path.join(TEST_FILES_FOLDER, "0_meta.json"), os.path.join(ASSETS_PATH, "0_meta.json"))

        cls.corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
        with open(cls.corpus_manager.get_articles()[0].get_meta_file_path(), 'r', encoding='utf-8') as meta_file:
            meta = json.load(meta_file)
        cls.frequencies = meta.pop('pos_frequencies')
        with open(cls.corpus_manager.get_articles()[0].get_meta_file_path(), 'w', encoding='utf-8') as meta_file:
            json.dump(meta,
                      meta_file,
                      sort_keys=False,
                      indent=4,
                      ensure_ascii=False,
                      separators=(',', ': '))

        pipe = TextProcessingPipeline(cls.corpus_manager)
        pipe.run()
        pos_pipe = POSFrequencyPipeline(cls.corpus_manager)
        pos_pipe.run()

    @pytest.mark.mark10
    @pytest.mark.stage_4_pos_frequency_pipeline_checks
    def test_meta_files_readable(self):
        failed = False
        try:
            article = self.corpus_manager.get_articles()[0]
            with open(article.get_meta_file_path(), 'r', encoding='utf-8') as meta_file:
                json.load(meta_file)
        except json.decoder.JSONDecodeError:
            failed = True
        finally:
            self.assertFalse(failed, 'Generated meta files are corrupt: check how you update .json files')

    @pytest.mark.mark10
    @pytest.mark.stage_4_pos_frequency_pipeline_checks
    def test_frequencies_are_correct(self):
        article = self.corpus_manager.get_articles()[0]
        with open(article.get_meta_file_path(), 'r', encoding='utf-8') as meta_file:
            frequencies = json.load(meta_file)['pos_frequencies']
        self.assertEqual(self.frequencies, frequencies, 'POS frequencies are calculated incorrectly')

    @pytest.mark.mark10
    @pytest.mark.stage_4_pos_frequency_pipeline_checks
    def test_tags_are_mystem(self):
        article = self.corpus_manager.get_articles()[0]
        with open(article.get_meta_file_path(), 'r', encoding='utf-8') as meta_file:
            pos_tags = json.load(meta_file)['pos_frequencies'].keys()
        for tag in pos_tags:
            self.assertTrue(tag in MYSTEM_TAGS,
                            msg=f"""Tag {tag} not in list of known mystem tags""")

    @pytest.mark.mark10
    @pytest.mark.stage_4_pos_frequency_pipeline_checks
    def test_images_are_generated(self):
        msg = 'POSFrequencyPipeline does not create image file for at least one of articles available'
        ids_available = set(list(map(lambda name: int(name.split('_')[0]), os.listdir(ASSETS_PATH))))
        for identifier in ids_available:
            self.assertTrue(os.path.exists(os.path.join(ASSETS_PATH, f'{identifier}_image.png')), msg)

    @pytest.mark.mark10
    @pytest.mark.stage_4_pos_frequency_pipeline_checks
    def test_empty_file_exception_thrown(self):
        msg1 = 'POSFrequencyPipeline does not throw exception when fed empty file'
        msg2 = 'POSFrequencyPipeline throws inappropriate exception when fed empty file'

        # create empty files with the unlikeliest to be reserved names
        chunks = ['_raw.txt', '_single_tagged.txt', '_multiple_tagged.txt']
        for chunk in chunks:
            with open(os.path.join(ASSETS_PATH, '1000' + chunk), 'w', encoding='utf-8') as file:
                file.write('')

        corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
        exception_is_thrown = False
        exception_is_correct = True

        try:
            POSFrequencyPipeline(corpus_manager=corpus_manager).run()
        except EmptyFileError:
            exception_is_thrown = True
        except Exception:
            exception_is_thrown = True
            exception_is_correct = False

        for chunk in chunks:
            os.remove(os.path.join(ASSETS_PATH, '1000' + chunk))

        self.assertTrue(exception_is_thrown, msg1)
        self.assertTrue(exception_is_correct, msg2)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(ASSETS_PATH)  # cleaning and restoring original ASSETS_PATH state
        shutil.copytree(TEST_TMP, ASSETS_PATH)
        shutil.rmtree(TEST_TMP)
