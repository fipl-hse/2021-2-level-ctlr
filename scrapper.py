"""
Scrapper implementation
"""
import requests
from bs4 import BeautifulSoup
import re
import json
import os


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
        url = 'https://vz.ru/news/'
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        try:
            for link in soup.find_all('a', attrs={'href': re.compile("^http[s]?://")}):
                print(link.get('href'))
        except KeyError:
            print('Incorrect link')

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
        os.rmdir(base_path)  # removing directory
    except FileNotFoundError:
        pass
    os.mkdir(base_path)  # creating directory


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']

    if not isinstance(seed_urls, list):
        raise IncorrectURLError

    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError

    for url in seed_urls:
        correct_url = re.match(r'https://', url)
        if not correct_url:
            raise IncorrectURLError

    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError

    if max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
