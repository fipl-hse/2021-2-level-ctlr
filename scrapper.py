"""
Scrapper implementation
"""
import os
import shutil
import json
import re
import random
from collections import namedtuple
from time import sleep
from constants import (HEADERS)
import requests
from bs4 import BeautifulSoup


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


class BadStatusCode(Exception):
    """
    Custom error
    """


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.total_max_articles = max_articles
        self.urls = []

    @staticmethod
    def _modify_link(link):
        if 'https://alp.iling.spb.ru/' not in link:
            link = 'https://alp.iling.spb.ru/' + link[2:]
        return link

    def _extract_url(self, article_bs):
        contents_bs = article_bs.select('div.content-cont-col-text a')
        links = [self._modify_link(article['href']) for article in contents_bs]
        return links

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            sleep(random.randrange(2, 5))

            if not response.status_code == 200:
                raise BadStatusCode

            soup = BeautifulSoup(response.text, 'lxml')  # install and add lxml to requirements.txt
            articles = self._extract_url(soup)[:self.total_max_articles]
            return articles

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    os.mkdir(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

        n_articles = config['total_articles_to_find_and_parse']
        is_n_articles = isinstance(n_articles, int)
        is_n_in_range = 0 < n_articles < 1000

        seed_urls = config['seed_urls']
        pattern = re.compile(r'https://alp\.iling\.spb\.ru/.+')
        is_seed_urls = isinstance(seed_urls, list)
        if is_seed_urls:
            is_seed_urls = all(pattern.match(str(x)) for x in seed_urls)

        Validation = namedtuple('Validation', ['success', 'error'])
        validations = (
            Validation(is_n_articles, IncorrectNumberOfArticlesError),
            Validation(is_n_in_range, NumberOfArticlesOutOfRangeError),
            Validation(is_seed_urls, IncorrectURLError)
        )

        for test in validations:
            if not test.success:
                raise test.error

        return seed_urls, n_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
