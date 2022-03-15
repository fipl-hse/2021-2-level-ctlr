"""
Scrapper implementation
"""

import requests
import json
import os
import re
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH


class IncorrectURLError(Exception):
    """
    Seed URL does not match standard pattern
    """


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Total number of articles to parse is too big
    """


class IncorrectNumberOfArticlesError(Exception):
    """
    Total number of articles to parse in not integer
    """


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
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/'
                      'avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6'}

        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=headers)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
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
    try:
        with open(crawler_path, 'r', encoding='utf-8') as config:
            conf = json.load(config)

        seed_urls = conf["seed_urls"]
        max_articles = conf["total_articles_to_find_and_parse"]

        for url in seed_urls:
            right_url = re.match(r'https?://', url)
            if not right_url:
                raise IncorrectURLError

        if not isinstance(max_articles, int):
            raise IncorrectNumberOfArticlesError

        if max_articles > 200:
            raise IncorrectNumberOfArticlesError

    except IncorrectURLError:
        print('Incorrect URL')
    except NumberOfArticlesOutOfRangeError:
        print('Number of articles out of range')
    except IncorrectNumberOfArticlesError:
        print('Incorrect number of articles')


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
