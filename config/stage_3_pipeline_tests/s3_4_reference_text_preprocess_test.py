import re
from string import punctuation
import unittest

import pytest
import shutil

from constants import ASSETS_PATH
from pipeline import CorpusManager, TextProcessingPipeline, validate_dataset
from config.test_params import TEST_FILES_FOLDER


MYSTEM_TAGS = ["A", "ADV", "S", "V", "PR", "ANUM"]
PYMORPHY_TAGS = ["ADJF", "PREP", "NOUN", "ADVB"]


class ReferenceTextPreprocessTestSimplified(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        validate_dataset(ASSETS_PATH)
        shutil.copyfile(TEST_FILES_FOLDER / "0_raw.txt", ASSETS_PATH / "0_raw.txt")
        corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
        pipe = TextProcessingPipeline(corpus_manager)
        pipe.run()

    def setUp(self) -> None:
        with (TEST_FILES_FOLDER / 'reference_score_four_test.txt').open('r', encoding='utf-8') as rf:
            self.reference = rf.read()
        with (ASSETS_PATH / "0_cleaned.txt").open("r", encoding='utf-8') as pr:
            self.processed = pr.read()

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_reference_preprocessed_are_equal(self):
        # check number of tokens sequences
        self.assertEqual(len(self.reference.split()),
                         len(self.processed.split()),
                         msg=f"""Number of tokens sequences in reference {self.reference} 
                                                and processed {self.processed} texts is different""")

        # check tokenization
        self.assertEqual(self.reference.split(),
                         self.processed.split(),
                         msg="""Pipe does not tokenize admin text. Check how you tokenize""")

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_overall_format(self):
        self.assertTrue(self.processed.islower(),
                        'Cleaned text must be lowercased')
        self.assertFalse((set(self.processed) & set(punctuation)),
                         'Cleaned text must not have any punctuation')

    @classmethod
    def tearDownClass(cls) -> None:
        (ASSETS_PATH / "0_raw.txt").unlink()
        (ASSETS_PATH / "0_cleaned.txt").unlink()
        if (ASSETS_PATH / "0_single_tagged.txt").exists():
            (ASSETS_PATH / "0_single_tagged.txt").unlink()
            if (ASSETS_PATH / "0_multiple_tagged.txt").exists():
                (ASSETS_PATH / "0_multiple_tagged.txt").unlink()


class ReferenceTextPreprocessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        validate_dataset(ASSETS_PATH)
        shutil.copyfile(TEST_FILES_FOLDER / "0_meta.json", ASSETS_PATH / "0_meta.json")
        shutil.copyfile(TEST_FILES_FOLDER / "0_raw.txt", ASSETS_PATH / "0_raw.txt")
        corpus_manager = CorpusManager(path_to_raw_txt_data=ASSETS_PATH)
        pipe = TextProcessingPipeline(corpus_manager)
        pipe.run()

    def setUp(self) -> None:
        with (TEST_FILES_FOLDER / 'reference_test.txt').open('r', encoding='utf-8') as rf:
            self.single_tagged_reference = rf.read()
        with (ASSETS_PATH / "0_single_tagged.txt").open("r", encoding='utf-8') as pr:
            self.single_tagged_processed = pr.read()
        self.mystem_tag_pattern = r"[а-яa-z]+<"

        if (ASSETS_PATH / "0_multiple_tagged.txt").exists():
            with (ASSETS_PATH / "0_multiple_tagged.txt").open("r", encoding='utf-8') as pr:
                self.multiple_tagged_processed = pr.read()
            with (TEST_FILES_FOLDER / 'reference_score_eight_test.txt').open('r', encoding='utf-8') as rf:
                self.multiple_tagged_reference = rf.read()
        self.pymorphy_tag_pattern = r"\w+<*>\(*\)"

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_single_tagged_reference_preprocessed_are_equal(self):
        # check number of token word<tag> sequences
        self.assertEqual(len(re.findall(self.mystem_tag_pattern, self.single_tagged_reference)),
                         len(re.findall(self.mystem_tag_pattern, self.single_tagged_processed)),
                         msg=f"""Number of word<tag> sequences in reference {self.single_tagged_reference} 
                                                and processed {self.single_tagged_processed} texts is different""")

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_single_tagged_all_tokens_are_formatted(self):
        msg = 'In single-tagged files, all tokens must be accompanied by a single set of tags in angle brackets'
        self.assertEqual(len(re.findall(self.mystem_tag_pattern, self.single_tagged_processed)),
                         len(self.single_tagged_processed.split()),
                         msg)

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_single_tagged_overall_format(self):
        # check correctness of word<tag> sequences
        for word_tag in self.single_tagged_processed.split():
            self.assertEqual(word_tag[-1], ">",
                             msg=f"{word_tag} --- There should be > at the end of each word<tag> sequence")
            self.assertTrue("<" in word_tag,
                            msg=f"{word_tag} --- < markup symbol should be in processed text")
            self.assertTrue(word_tag[word_tag.index("<")-1].isalpha(),
                            msg=f"{word_tag} --- In tagged sequence there should be char symbol before < ")

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_single_tagged_mystem_tag_format(self):
        # check TAGS after each sequence:
        tags_pattern = r"<([A-Z]+)[,=]{1}"
        reference_tags = re.findall(tags_pattern, self.single_tagged_reference)
        processed_tags = re.findall(tags_pattern, self.single_tagged_processed)

        # check tag correctness.
        # Optional, but should be the same across each tagger, as reference example is too simple
        for tag in processed_tags:
            self.assertTrue(tag in MYSTEM_TAGS,
                            msg=f"Tag {tag} is an unknown Mystem tag. Is it in required tags list?")
        self.assertEqual(reference_tags, processed_tags,
                         msg=f"""Mystem tag sequence from reference text {reference_tags}
                                    differs from processed text {processed_tags}""")

    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_multiple_tagged_reference_preprocessed_are_equal(self):
        # check number of token word<tag> sequences
        self.assertEqual(len(self.multiple_tagged_reference.split()),
                         len(self.multiple_tagged_processed.split()),
                         msg=f"""Number of word<tag>(tag) sequences in reference {self.multiple_tagged_reference} 
                                                and processed {self.multiple_tagged_processed} texts is different""")

    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_multiple_tagged_overall_format(self):
        # check correctness of word<tag> sequences
        for word_tag in self.multiple_tagged_processed.split():
            try:
                self.assertEqual(word_tag[-1], ")",
                                 msg=f"{word_tag} --- There should be ) at the end of each word<tag>(tag) sequence")
            except AssertionError:
                self.assertTrue(word_tag[-1].isalpha())
            try:
                self.assertTrue("<" in word_tag,
                                msg=f"{word_tag} --- < markup symbol should be in processed text")
            except AssertionError:
                self.assertTrue(word_tag[0].isalpha() and (word_tag[-1] == ")"))
            try:
                self.assertTrue(word_tag[word_tag.index("<")-1].isalpha(),
                                msg=f"{word_tag} --- In tagged sequence there should be char symbol before < ")
            except ValueError:
                self.assertTrue(word_tag[0].isalpha() and (word_tag[-1] == ")"))
            try:
                self.assertEqual(word_tag[word_tag.index(">")+1], "(",
                                 msg=f"{word_tag} --- There should be ( after > in the word<tag>(tag) sequence")
            except ValueError:
                self.assertTrue(word_tag[0].isalpha() and (word_tag[-1] == ")"))

    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_multiple_tagged_tag_format(self):
        # check TAGS after each sequences:
        tags_pattern = r">\([A-Z]+"
        reference_tags = re.findall(tags_pattern, self.multiple_tagged_reference)
        processed_tags = re.findall(tags_pattern, self.multiple_tagged_processed)

        # check tag correctness.
        # Optional, but should be the same across each tagger, as reference example is too simple
        for tag in processed_tags:
            tag = tag[2:]
            self.assertTrue(tag in PYMORPHY_TAGS,
                            msg=f"Tag {tag} is an unknwon pymorphy tag. Is it in required tags list?")
        self.assertEqual(reference_tags, processed_tags,
                         msg=f"""Tag sequence from reference text {reference_tags}
                                    differs from processed text {processed_tags}""")

    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_multiple_tagged_mystem_tag_format(self):
        # check TAGS after each sequence:
        tags_pattern = r"<([A-Z]+)[,=]{1}"
        reference_tags = re.findall(tags_pattern, self.multiple_tagged_reference)
        processed_tags = re.findall(tags_pattern, self.multiple_tagged_processed)
        for tag in processed_tags:
            self.assertTrue(tag in MYSTEM_TAGS,
                            msg=f"Tag {tag} is an unknown Mystem tag. Is it in required tags list?")
        self.assertEqual(reference_tags, processed_tags,
                         msg=f"""Mystem tag sequence from reference text {reference_tags}
                                    differs from processed text {processed_tags}""")
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_4_admin_data_processing
    def test_pymorphy_tag_format(self):
        reference_tags = self.multiple_tagged_reference.split()
        processed_tags = self.multiple_tagged_processed.split()
        self.assertEqual(reference_tags, processed_tags,
                         msg=f"""Tag sequence from reference text {reference_tags}
                                            differs from processed text {processed_tags}""")

    @classmethod
    def tearDownClass(cls) -> None:
        (ASSETS_PATH / "0_meta.json").unlink()
        (ASSETS_PATH / "0_raw.txt").unlink()
        (ASSETS_PATH / "0_cleaned.txt").unlink()
        (ASSETS_PATH / "0_single_tagged.txt").unlink()
        if (ASSETS_PATH / "0_multiple_tagged.txt").is_file():
            (ASSETS_PATH / "0_multiple_tagged.txt").unlink()
