"""
Scrapper implementation
"""

import json
import os
import re

import requests
from bs4 import BeautifulSoup

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile


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

        for url in self.seed_urls:
            response = requests.get(url, headers=headers)

            if not response.ok:
                print("Request failed")

            soup = BeautifulSoup(response.text, 'lxml')

            articles = soup.find('div', class_='entry-content')
            all_links = articles.find_all('a')[1:]
            for link in all_links:
                try:
                    if (('https://vestnik.lunn.ru/' in link['href']) or
                            ('http://vestnik.lunn.ru/' in link['href'])):
                        self.urls.append(link['href'])
                    else:
                        self.urls.append('https://vestnik.lunn.ru/' + link['href'])
                except KeyError:
                    print('Found incorrect link')

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def parse(self):
        self.article = Article(self.article_url, self.article_id)

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/'
                      'avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6'}

        response = requests.get(self.article_url, headers)
        article_bs = BeautifulSoup(response.text, 'lxml')

        # self._fill_article_with_text(article_bs)
        # self.article.save_raw()
        return self.article

    def _fill_article_with_text(self, article_bs):
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
    with open(crawler_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    seed_urls = config["seed_urls"]
    max_articles = config["total_articles_to_find_and_parse"]

    for url in seed_urls:
        right_url = re.match(r'https?://', url)
        if not right_url:
            raise IncorrectURLError

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
