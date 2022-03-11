"""
Scrapper implementation
"""
import json
import re
import os
import requests
from constants import ASSETS_PATH


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
        # html = "https://languagejournal.spbu.ru/issue/view/682"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) " \
                     "Gecko/20100101 Firefox/99.0"
        accept = "*/*"
        accept_encoding = "gzip, deflate, br"
        accept_language = "en-US,en;q=0.5"
        headers = \
            {
                'User-Agent': user_agent,
                'Accept': accept,
                'Accept-Encoding': accept_encoding,
                'Accept-Language': accept_language
            }
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=headers)
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
        with open(crawler_path) as file:
            config = json.load(file)

        seed_urls = config["seed_urls"]
        total_articles = config["total_articles_to_find_and_parse"]

        for seed_url in seed_urls:
            if not re.match(r'https?://', seed_url):
                raise IncorrectURLError

        if not isinstance(total_articles, int):
            raise IncorrectNumberOfArticlesError

        if total_articles > 300:
            raise NumberOfArticlesOutOfRangeError

        prepare_environment(ASSETS_PATH)

        return seed_urls, total_articles

    except IncorrectURLError:
        print("IncorrectURLError")
    except NumberOfArticlesOutOfRangeError:
        print("NumberOfArticlesOutOfRangeError")
    except IncorrectNumberOfArticlesError:
        print("IncorrectNumberOfArticlesError")


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
