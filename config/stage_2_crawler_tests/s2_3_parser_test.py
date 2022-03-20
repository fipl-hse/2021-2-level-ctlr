
import json
import random
import unittest

import pytest

from core_utils.article import Article
from scrapper import validate_config, Crawler, HTMLParser
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH


class HTMLParserTest(unittest.TestCase):

    def setUp(self) -> None:
        validate_config(CRAWLER_CONFIG_PATH)
        with open(CRAWLER_CONFIG_PATH, encoding='utf-8') as file:
            data = json.load(file)

        if not ASSETS_PATH.exists():
            ASSETS_PATH.mkdir(parents=True)

        self.crawler = Crawler(data['seed_urls'],
                               data['total_articles_to_find_and_parse'])
        self.crawler.find_articles()
        self.parser = HTMLParser(random.choice(self.crawler.urls), 1)
        self.return_value = self.parser.parse()

    def tearDown(self) -> None:
        for pdf_file in ASSETS_PATH.glob('*.pdf'):
            print(f'Removing {pdf_file}')
            pdf_file.unlink()

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_3_HTML_parser_check
    def test_HTML_parser_instantiation(self):
        parser = HTMLParser(random.choice(self.crawler.urls), 1)
        self.assertTrue(hasattr(parser, 'article'), "Parser instance must possess 'article' attribute")
        self.assertIsInstance(parser.article, Article, "Attribute 'article' of Parser instance must be \
an instance of Article")

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_3_HTML_parser_check
    def test_HTML_parser_parse_return_value_basic(self):
        self.assertIsInstance(self.return_value, Article, "parse() method must return Article instance")
        self.assertTrue(self.return_value.article_id, "parse() method must return Article with filled id")
        self.assertTrue(self.return_value.text, "parse() method must return an Article instance with filled text")

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_3_HTML_parser_check
    def test_HTML_parser_parse_return_value_medium(self):
        self.assertTrue(self.return_value.title, "parse() method must return Article with filled title")
        self.assertTrue(self.return_value.author, "parse() method must return an Article instance with filled author")

    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_3_HTML_parser_check
    def test_HTML_parser_parse_method_advanced(self):
        self.assertTrue(self.return_value.date, "parse() method must return an Article instance with filled date")
