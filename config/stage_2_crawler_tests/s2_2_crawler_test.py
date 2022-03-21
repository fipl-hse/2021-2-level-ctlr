import json
import unittest

import pytest

from scrapper import validate_config, Crawler
from constants import CRAWLER_CONFIG_PATH


class CrawlerTest(unittest.TestCase):

    def setUp(self) -> None:
        validate_config(CRAWLER_CONFIG_PATH)
        with CRAWLER_CONFIG_PATH.open(encoding='utf-8') as file:
            data = json.load(file)
            self.total_number = data['total_articles_to_find_and_parse']
            self.seed = data['seed_urls']

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_2_crawler_check
    def test_newly_created_crawler_instance_empty(self):
        crawler = Crawler(self.seed, self.total_number)
        error_msg = 'Check Crawler constructor: field "urls" is supposed to initially be empty'
        self.assertFalse(crawler.urls, error_msg)

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_2_crawler_check
    def test_crawler_instance_is_filled_from_find_articles(self):
        crawler = Crawler(self.seed, self.total_number)
        crawler.find_articles()
        error_msg = 'Method find_articles() must fill field "urls" with links found with the help of seed URLs'
        self.assertTrue(crawler.urls, error_msg)

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_2_crawler_check
    def test_crawler_instance_stores_full_urls(self):
        crawler = Crawler(self.seed, self.total_number)
        crawler.find_articles()
        error_msg = 'Method find_articles() must fill field "urls" with ready-to-use full links with http'
        self.assertFalse(list(filter(lambda url: 'http' not in url, crawler.urls)), error_msg)

    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_2_crawler_check
    def test_crawler_finds_required_number_of_articles(self):
        crawler = Crawler(self.seed, self.total_number)
        crawler.find_articles()
        error_msg = 'Method find_articles() must fill field "urls" with not less articles than specified in config file'
        self.assertTrue(len(crawler.urls) >= self.total_number, error_msg)
