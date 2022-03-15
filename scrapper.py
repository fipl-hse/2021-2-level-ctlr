"""
Scrapper implementation
"""
import json
import os
import re
import requests
from bs4 import BeautifulSoup
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
    def __init__(self, article_urls, total_articles: int):
        self.article_urls = article_urls
        self.total_articles = total_articles
        self.urls = []

    def _extract_url(self, article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        for article_url in self.article_urls:
            response = requests.get(article_url)
            # with open('index.html', 'w', encoding='utf-16') as file:
            #     file.write(response.text)
            if not response.ok:
                print('Response is failed')
            soup = BeautifulSoup(response.text, 'html.parser')
            all_links = soup.find_all('a')
            for link in all_links:
                self.urls.append('https://daily-nn.ru' + link['href'])

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


# class Article:
#     def __init__(self, article):
#         self.article = article
#
#
# class HTMLParser:
#     def __init__(self, article_url, article_id):
#         self.article_url = article_url
#         self.article_id = article_id
#
#     def _fill_article_with_text(self, article_bs):
#         self.article_bs = article_bs
#
#     def parse(self):
#         response = requests.get(self.article_url)
#         article_bs = BeautifulSoup(response.text, 'html.parser')
#         self._fill_article_with_text(article_bs)


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
    with open(crawler_path, 'r') as file:
        config = json.load(file)
    article_urls = config['seed_urls']
    if not isinstance(article_urls, list):
        raise IncorrectURLError
    for article_url in article_urls:
        correct_url = re.match(r'https://', article_url)
        if not correct_url:
            raise IncorrectURLError
    total_articles = config['total_articles_to_find_and_parse']
    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError
    if total_articles > 100 or total_articles <= 0:
        raise NumberOfArticlesOutOfRangeError
    return article_urls, total_articles


if __name__ == '__main__':
    seed_urls, max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls=seed_urls, total_max_articles=max_articles)
    crawler.find_articles()
