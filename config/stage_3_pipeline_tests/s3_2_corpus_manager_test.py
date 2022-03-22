import json
import unittest

import pytest
import shutil

from core_utils.article import Article
from constants import ASSETS_PATH
from pipeline import CorpusManager, validate_dataset
from config.test_params import TEST_FILES_FOLDER


class ArticleInstanceCreationBasicTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        validate_dataset(ASSETS_PATH)
        shutil.copyfile(TEST_FILES_FOLDER / "0_raw.txt", ASSETS_PATH / "0_raw.txt")

    def setUp(self) -> None:
        self.corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_2_corpus_manager_checks
    def test_corpus_manager_instantiation(self):
        self.assertTrue(hasattr(self.corpus_manager, '_storage'), 'CorpusManager instance must have _storage field')
        self.assertIsInstance(self.corpus_manager._storage, dict,
                              'CorpusManager attribute _storage must be dict object')
        self.assertTrue(self.corpus_manager._storage,
                        'CorpusManager attribute _storage must be filled right away during initialisation')

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_2_corpus_manager_checks
    def test_raw_files_are_found(self):
        self.assertIn(0, self.corpus_manager._storage,
                      "Corpus Manager does not create article instances given raw files only")

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_2_corpus_manager_checks
    def test_article_instance_is_created(self):
        self.assertIsInstance(self.corpus_manager._storage[0], Article,
                              "CorpusManager _storage values must be Article instances")

    @classmethod
    def tearDownClass(cls) -> None:
        (ASSETS_PATH / "0_raw.txt").unlink()


class ArticleInstanceCreationAdvancedTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        validate_dataset(ASSETS_PATH)
        shutil.copyfile(TEST_FILES_FOLDER / "0_meta.json", ASSETS_PATH / "0_meta.json")
        shutil.copyfile(TEST_FILES_FOLDER / "0_raw.txt", ASSETS_PATH / "0_raw.txt")

    def setUp(self) -> None:
        self.corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
        with (TEST_FILES_FOLDER / '0_meta.json').open(encoding='utf-8') as f:
            self.meta = json.load(f)

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_2_corpus_manager_checks
    def test_meta_files_are_found(self):
        self.assertIn(0, self.corpus_manager._storage,
                      "Corpus Manager does not create article instances given both raw and meta files")

    @classmethod
    def tearDownClass(cls) -> None:
        (ASSETS_PATH / "0_raw.txt").unlink()
        (ASSETS_PATH / "0_meta.json").unlink()
