"""
Scrapper implementation
"""
import json
import re
import os
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


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.urls = []

    def _extract_url(self, article_bs):

        all_links = article_bs.find_all('a')
        for link in all_links:
            try:
                href = link['href']
                if re.match(r'http', href):  # checks if there is a domain at the beginning of url
                    self.urls.append(href)
                    print(href)
                else:
                    href = 'https://lingngu.elpub.ru/' + href
                    self.urls.append(href)
                    print(href)
            except KeyError:
                print('Incorrect link or no href found')

    def find_articles(self):
        """
        Finds articles
        """
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/99.0.4844.51 Safari/537.36'}

        for url in self.seed_urls:
            response = requests.get(url, headers)  # get html code
            article_bs = BeautifulSoup(response.text, 'html.parser')  # creates BS object
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.rmdir(base_path)  # removes a folder
    except FileNotFoundError:
        os.mkdir(base_path)  # creates new one if it doesn't exist


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)  # load is for decoding

    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError

    for url in seed_urls:
        if not re.match(r'https?://', url):  # https or http
            raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
