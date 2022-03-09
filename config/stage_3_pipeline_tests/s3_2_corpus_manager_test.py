import os
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
        shutil.copyfile(os.path.join(TEST_FILES_FOLDER, "0_raw.txt"), os.path.join(ASSETS_PATH, "0_raw.txt"))

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

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_2_corpus_manager_checks
    def test_article_instance_fields_are_empty(self):

        article = self.corpus_manager._storage[0]
        msg = "Fields of Article instances created by CorpusManager must me empty unless meta files are available"
        self.assertFalse(any((article.title,
                              article.author,
                              article.topics,
                              article.date,
                              article.text)),
                         msg)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(os.path.join(ASSETS_PATH, "0_raw.txt"))


class ArticleInstanceCreationAdvancedTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        validate_dataset(ASSETS_PATH)
        shutil.copyfile(os.path.join(TEST_FILES_FOLDER, "0_meta.json"), os.path.join(ASSETS_PATH, "0_meta.json"))
        shutil.copyfile(os.path.join(TEST_FILES_FOLDER, "0_raw.txt"), os.path.join(ASSETS_PATH, "0_raw.txt"))

    def setUp(self) -> None:
        self.corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
        with open(os.path.join(TEST_FILES_FOLDER, '0_meta.json'), encoding='utf-8') as f:
            self.meta = json.load(f)

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_2_corpus_manager_checks
    def test_meta_files_are_found(self):
        self.assertIn(0, self.corpus_manager._storage,
                      "Corpus Manager does not create article instances given both raw and meta files")

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_2_corpus_manager_checks
    def test_article_instance_fields_are_filled(self):

        student_meta = self.corpus_manager._storage[0]._get_meta()

        message = '{field_name} field of newly created article instance differs from corresponding {field_name} \
value in meta file'

        self.assertEqual(student_meta.get('id'), self.meta.get('id'), message.format(field_name='Id'))
        self.assertEqual(student_meta.get('url'), self.meta.get('url'), message.format(field_name='URL'))
        self.assertEqual(student_meta.get('title'), self.meta.get('title'), message.format(field_name='title'))
        self.assertEqual(student_meta.get('author'), self.meta.get('author'), message.format(field_name='author'))
        self.assertEqual(student_meta.get('topics'), self.meta.get('topics'), message.format(field_name='topics'))

        self.assertFalse(student_meta.get('text'), 'Text field of newly created article instance must be empty')

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(os.path.join(ASSETS_PATH, "0_raw.txt"))
        os.remove(os.path.join(ASSETS_PATH, "0_meta.json"))
