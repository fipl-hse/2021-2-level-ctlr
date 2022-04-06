import re
import unittest

import pytest

from constants import ASSETS_PATH


MYSTEM_TAGS = ['A', 'ADV', 'ADVPRO', 'ANUM', 'APRO', 'COM', 'CONJ', 'INTJ', 'NUM', 'PART', 'PR', 'S', 'SPRO', 'V']
PYMORPHY_TAGS = ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND',
                 'NUMR', 'ADVB', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ', 'UNKN']

PUNCTUATION_MARKS = [',', '.', '-', ';', ':', '!', '?', '<']


class StudentTextBasicPreprocessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.articles = dict()
        for article in ASSETS_PATH.iterdir():
            if article.name.endswith("_cleaned.txt"):
                with article.open("r", encoding="utf-8") as txt:
                    self.articles[int(article.name[:-12])] = txt.read()

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_5_student_dataset_validation
    def test_clean_tokens(self):
        for article_id, article_text in self.articles.items():
            for token in article_text.split():
                self.assertTrue(token not in PUNCTUATION_MARKS,
                                msg=f"""There are some punctuation marks found in article {article_id}""")
                self.assertTrue(token.islower(),
                                msg=f"""Token {token} in article {article_id} is not lowercased""")


class StudentTextAdvancedPreprocessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.articles = dict()
        for article in ASSETS_PATH.iterdir():
            if article.name.endswith("_multiple_tagged.txt"):
                with article.open("r", encoding="utf-8") as txt:
                    self.articles[int(article.name[:-20])] = txt.read()

    @staticmethod
    def custom_split(string) -> list:
        return [element+')' for element in string.split(') ')]

    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_5_student_dataset_validation
    def test_multiple_tagged_tokens_format(self):
        for article_id, article_text in self.articles.items():
            word_tag_sequences = self.custom_split(article_text)
            for sequence in word_tag_sequences:
                self.assertTrue("(" in sequence,
                                msg=f"{sequence} --- ( markup symbol should be in processed text")
                self.assertEqual(sequence[sequence.rindex("(") - 1], ">",
                                 msg=f"{sequence} --- In tagged sequence there should be > symbol before ( ")

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_5_student_dataset_validation
    def test_mystem_tags_correctness_multiple_tagged(self):
        for article_id, article_text in self.articles.items():
            tags = re.findall(r"<([A-Z]+)[,=]?", article_text)
            for tag in tags:
                self.assertTrue(tag in MYSTEM_TAGS,
                                msg=f"""Tag {tag} not in list of known mystem tags""")

    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_5_student_dataset_validation
    def test_pymorphy_tags_correctness_multiple_tagged(self):
        for article_id, article_text in self.articles.items():
            tags = re.findall(r"\([A-Z]+", article_text)
            for tag in tags:
                tag = tag[1:]
                self.assertTrue(tag in PYMORPHY_TAGS,
                                msg=f"""Tag {tag} not in list of known pymorphy tags""")


class StudentTextMediumPreprocessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.articles = dict()
        for article in ASSETS_PATH.iterdir():
            if article.name.endswith("_single_tagged.txt"):
                with article.open("r", encoding="utf-8") as txt:
                    self.articles[int(article.name[0])] = txt.read()

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_5_student_dataset_validation
    def test_single_tagged_tokens_format(self):
        for article_id, article_text in self.articles.items():
            word_tag_sequences = article_text.split()
            for sequence in word_tag_sequences:
                self.assertTrue(sequence.endswith(">"),
                                msg=f"{sequence} --- There should be > at the end of each word<tag> sequence")
                self.assertIn("<", sequence,
                              msg=f"{sequence} --- < markup symbol should be in processed text")
                self.assertTrue(sequence[sequence.index("<") - 1].isalpha(),
                                msg=f"{sequence} --- In tagged sequence there should be char symbol before < ")

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_5_student_dataset_validation
    def test_mystem_tags_correctness_single_tagged(self):
        for article_id, article_text in self.articles.items():
            tags = re.findall(r"<([A-Z]+)[,=]?", article_text)
            for tag in tags:
                self.assertTrue(tag in MYSTEM_TAGS,
                                msg=f"""Tag {tag} not in list of known mystem tags""")
