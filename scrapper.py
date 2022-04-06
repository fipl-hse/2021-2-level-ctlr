"""
Scrapper implementation
"""
from datetime import datetime
import json
import re
import shutil
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, HEADERS
from core_utils.article import Article


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
        links = article_bs.find_all('div', class_='mnname')
        the_beginning = 'http://www.selsknov.ru'
        for url_bs in links:
            the_end = url_bs.find('a')['href']
            full_url = the_beginning + the_end
            if len(self.urls) < self.max_articles and full_url not in self.urls:
                self.urls.append(full_url)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=HEADERS)
            response.encoding = 'windows-1251'
            if not response.ok:
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            self._extract_url(soup)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_meta_information(self, article_bs):
        article_title = article_bs.find('div', class_="mnname").text
        self.article.title = article_title.strip()

        date = article_bs.find('div', class_='mndata')
        self.article.date = datetime.strptime(date.text, '%d.%m.%Y')

        try:
            author = article_bs.find('em')
            if "\xa0" in author.text:
                self.article.author = author.text.replace("\xa0", "NOT FOUND")
            else:
                if len(author.text) < 40:
                    self.article.author = author.text
                else:
                    self.article.author = "NOT FOUND"
        except AttributeError:
            self.article.author = "NOT FOUND"

        topic = article_bs.find("h1")
        self.article.topics = topic.text.strip()

    def _fill_article_with_text(self, article_bs):
        article_text = article_bs.find_all("font")
        self.article.text = ''
        for text in article_text:
            self.article.text += text.text

    def parse(self):
        response = requests.get(self.article_url, headers=HEADERS)
        response.encoding = 'windows-1251'
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = Path(base_path)
    if path.exists():
        shutil.rmtree(base_path)
    path.mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration = json.load(file)

    seed_urls = configuration['seed_urls']
    max_articles = configuration['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    part_of_string = re.compile(r'^https?://')
    for seed_url in seed_urls:
        if not part_of_string.search(seed_url):
            raise IncorrectURLError

    return seed_urls, max_articles


if __name__ == '__main__':
    seed_urls_test, max_articles_test = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(seed_urls_test, max_articles_test)
    crawler.find_articles()

    ID = 0
    for article_url_text in crawler.urls:
        ID += 1
        article_parser = HTMLParser(article_url_text, ID)
        article = article_parser.parse()
        article.save_raw()
