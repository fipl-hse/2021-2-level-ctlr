"""
Scrapper implementation
"""
import json
import re
import os
import requests
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH


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
        os.rmdir(base_path)  # removes a folder
    except FileNotFoundError:
        os.mkdir(base_path)  # creates new if it doesn't exist


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as dictionary:
        config = json.load(dictionary)  # load is for decoding

    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']

    for url in seed_urls:
        if not re.match(r'https?://', url):  # https or http
            raise IncorrectURLError('IncorrectURLError')

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError('NumberOfArticlesOutOfRangeError')

    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError('IncorrectNumberOfArticlesError')

    return seed_urls, max_articles


'''
    html = 'https://lingngu.elpub.ru/jour/issue/view/18/showToc'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/99.0.4844.51 Safari/537.36'}

    response = requests.get(html, headers)
    page_code = response.text

    with open('page_code.html', 'w', encoding='utf-8') as file:
        file.write(page_code)'''


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
