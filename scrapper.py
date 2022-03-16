"""
Scrapper implementation
"""
import os
import json
import re

import requests
from bs4 import BeautifulSoup

from constants import CRAWLER_CONFIG_PATH
from constants import HEADERS
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
        content_bs = article_bs.find_all('div', class_="issueArticle flex")
        for tag in content_bs:
            link = tag.find('a')
            main_link = link['href']
            self.urls.append(main_link)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, HEADERS)
            article_bs = BeautifulSoup(response.text, 'html.parser')
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as config:
        scrapper_config = json.load(config)

    seed_urls = scrapper_config["seed_urls"]
    total_articles_to_find_and_parse = scrapper_config["total_articles_to_find_and_parse"]

    if not isinstance(seed_urls, list):
        raise IncorrectURLError
    if not seed_urls:
        raise IncorrectURLError
    for seed_url in seed_urls:
        if not re.match('https://', seed_url):
            raise IncorrectURLError

    if not isinstance(total_articles_to_find_and_parse, int) or total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse > 300:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles_to_find_and_parse


class HTMLParser:
    """
    Parser implementation
    """

    def __init__(self, article_url, article_id):
        """
        Init
        """
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(url=article_url, article_id=article_id)

    def _fill_article_with_text(self, article_bs):

        table_rows = article_bs.find('div', class_="fulltext")
        link = table_rows.find('a')['href']
        new_link = re.sub(r'(?i)view(?=\W)', 'download', link)
        pdf_file = PDFRawFile(new_link, self.article_id)
        pdf_file.download()
        self.article.text = pdf_file.get_text()
        self.article.save_raw()

    def _fill_article_with_meta_information(self, article_bs):

        authors = []
        table_rows = article_bs.find('em')
        tag = table_rows.find_all('a')
        for title in tag:
            try:
                author = title["title"]
            except KeyError:
                continue
            authors.append(author)
        self.article.author = ', '.join(authors)

        table_rows1 = article_bs.find('h1')
        self.article.title = table_rows1.text

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()
        return self.article


if __name__ == '__main__':
    pass
