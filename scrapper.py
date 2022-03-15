"""
Scrapper implementation
"""

import json
import re
import os
import time
import requests
from bs4 import BeautifulSoup
# from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH


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
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru,en;q=0.9,de;q=0.8'
        }

        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=headers)
            time.sleep(3)
            if not response.ok:
                print("Something went wrong...")
            soup = BeautifulSoup(response.text, "lxml")
            main_block_bs = soup.find('div', {'class': 'cat-children'})
            for link in main_block_bs.find_all("a"):
                self.urls.append('https://l.jvolsu.com/' + link.get('href'))


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
    with open(crawler_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    seed_urls = config["seed_urls"]
    number_of_articles = config["total_articles_to_find_and_parse"]
    if not seed_urls or not isinstance(seed_urls, list):
        raise IncorrectURLError
    for seed_url in seed_urls:
        if not isinstance(seed_url, str):
            raise IncorrectURLError
        norm_url = re.match(r"https?://", seed_url)
        if not norm_url:
            raise IncorrectURLError
    if not isinstance(number_of_articles, int) or number_of_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if number_of_articles > 200:
        raise NumberOfArticlesOutOfRangeError
    return seed_urls, number_of_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
