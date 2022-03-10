"""
Scrapper implementation
"""

import json
import os
import re

import requests

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
            'User-Agent': """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 
            (KHTML, like Gecko) Chrome"""
                          '/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70',
            'Accept': """text/html,application/xhtml+xml,application/xml;q=0.9,
            image/avif,image/webp,image/apng,*/*;"""
                      'q=0.8,applicat '
                      'ion/signed-exchange;v=b3;q=0.9',
            'Acccept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=headers)
            with open(ASSETS_PATH, 'w', encoding='utf-8') as file:
                file.write(response.text)
            self.urls.append(seed_url)

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
        max_articles = data["total_articles_to_find_and_parse"]

        for url in seed_urls:
            url_validation = re.match(r'https?://', url)
            if not url_validation:
                raise IncorrectURLError

        if not isinstance(max_articles, int):
            raise IncorrectNumberOfArticlesError

        if max_articles > 300:
            raise NumberOfArticlesOutOfRangeError

        prepare_environment(ASSETS_PATH)

        return seed_urls, max_articles

    except IncorrectURLError:
        print('Incorrect URL')
    except IncorrectNumberOfArticlesError:
        print('Incorrect number of articles error')
    except NumberOfArticlesOutOfRangeError:
        print('Number of articles out of range')


crawler = Crawler(validate_config(CRAWLER_CONFIG_PATH)[0], validate_config(CRAWLER_CONFIG_PATH)[1])


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
