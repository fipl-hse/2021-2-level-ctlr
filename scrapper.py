"""
Scrapper implementation
"""

import json
import os
import re
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH


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
        pass

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
        os.rmdir(base_path)
    except FileNotFoundError:
        os.mkdir(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    try:
        with open(crawler_path, 'r', encoding='utf-8') as config:
            data = json.load(config)

        seed_urls = data["seed_urls"]
        number_of_articles = data["total_articles_to_find_and_parse"]

        for url in seed_urls:
            url_validation = re.match(r'http://.*|https://.*', url)
            if not url_validation:
                raise IncorrectURLError

        if not isinstance(number_of_articles, int):
            raise IncorrectNumberOfArticlesError

        if number_of_articles > 300:
            raise NumberOfArticlesOutOfRangeError

        return seed_urls, number_of_articles

    except IncorrectURLError:
        print('Incorrect URL')
    except IncorrectNumberOfArticlesError:
        print('Incorrect number of articles error')
    except NumberOfArticlesOutOfRangeError:
        print('Number of articles out of range')

    prepare_environment(ASSETS_PATH)


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
