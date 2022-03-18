"""
Scrapper implementation
"""
import json
import re
from pathlib import Path
import requests
from constants import ASSETS_PATH

class IncorrectURLError(Exception):
    """
    Seed URL does not match standard pattern
    """
    pass


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
        pass

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
        Path.rmdir(base_path)
    except FileNotFoundError:
        Path.mkdir(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    try:
        with open(crawler_path) as file:
            config = json.load(file)

        seed_urls = config["seed_url"]
        max_articles = config["total_articles_to find_and_parse"]

        if not isinstance(seed_urls, list) or not seed_urls:
            raise IncorrectURLError

        for url in seed_urls:
            validation = re.match(r'https?://', url)
            if not validation:
                raise IncorrectURLError

        if not isinstance(max_articles, int) or max_articles <= 0:
            raise IncorrectNumberOfArticlesError

        if max_articles > 300:
            raise NumberOfArticlesOutOfRangeError

        return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
