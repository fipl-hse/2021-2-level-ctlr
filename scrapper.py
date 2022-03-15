"""
Scrapper implementation
"""

import json
import os
import re

import requests
from bs4 import BeautifulSoup

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from core_utils import article


class IncorrectURLError(Exception):
    """
    Seed URL does not match standard pattern
    """
    pass


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Total number of articles to parse is too big
    """
    pass


class IncorrectNumberOfArticlesError(Exception):
    """
    Total number of articles to parse in not integer
    """
    pass


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                      'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru,en-GB;q=0.9,en;q=0.8,en-US;q=0.7'
        }

        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=headers)
            if not response.ok:
                print('request failed')

            self.urls.append(seed_url)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class ArticleParser:
    def __init__(self, full_url, i):
        self.article_url = full_url
        self.article_id = i
        self.article = article.Article

    def _fill_article_with_text(self, article_bs):
        pass

    """def parse(self):
        web_page = requests.get(self.article_url, headers=)"""


class HTMLParser:
    pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.rmdir(base_path)
    except FileNotFoundError:
        os.mkdir(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as config:
        data = json.load(config)

    seed_urls = data["seed_urls"]
    max_articles = data["total_articles_to_find_and_parse"]

    if not isinstance(seed_urls, list):
        raise IncorrectURLError
    if not seed_urls:
        raise IncorrectURLError
    for url in seed_urls:
        url_validation = re.match(r'https?://', url)
        if not url_validation:
            raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 300:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


#  crawler = Crawler(validate_config(CRAWLER_CONFIG_PATH)[0],
#  validate_config(CRAWLER_CONFIG_PATH)[1])


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
