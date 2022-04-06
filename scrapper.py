"""
Scrapper implementation
"""
import os
import json
import re
import random
from time import sleep
import requests
from bs4 import BeautifulSoup

from datetime import datetime
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
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
        self.max_articles = max_articles
        self.seed_urls = seed_urls
        self.urls = []

    def _extract_url(self, article_bs):
        urls_bs = article_bs.find_all('div', class_="item__wrap l-col-center")
        urls_bs_all = []

        for url_bs in urls_bs:
            url = url_bs.find('a')['href']
            urls_bs_all.append(url)
        for link in urls_bs_all:
            if len(self.urls) < self.max_articles:
                self.urls.append(link)

        return self.urls

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(random.randint(1, 5))

            response = requests.get(seed_url)

            if not response.ok:
                continue

            soup_lib = BeautifulSoup(response.text, 'lxml')

            self._extract_url(soup_lib)

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
        self.article.title = article_bs.find('h1', class_='article__header__title-in js-slide-title').text
        a_author = article_bs.find('a', class_='article__authors__author')
        self.article.author = a_author.text

        a_date = article_bs.find('span', class_="article__header__date").text

        months = {"января": "01",
                  "февраля": "02",
                  "марта": "03",
                  "апреля": "04",
                  "мая": "05",
                  "июня": "06",
                  "июля": "07",
                  "августа": "08",
                  "сентября": "09",
                  "октября": "10",
                  "ноября": "11",
                  "декабря": "12"}
        for month in months:
            if month in a_date:
                a_date = a_date.replace(month, months[month])
        self.article.date = datetime.strptime(a_date, '%H:%M, %d %m %Y')

    def _fill_article_with_text(self, article_bs):
        texts = article_bs.find('div', class_='article__text article__text_free')

        inner_blocks_1 = texts.find_all('div', class_='article__text__overview')
        for inner_block_1 in inner_blocks_1:
            overview_texts = inner_block_1.find_all('span')
            for overview_text in overview_texts:
                self.article.text += overview_text.text.strip()

        for text in texts:
            paragraphs_1 = text.find_all('p')
            for paragraph_1 in paragraphs_1:
                self.article.text += paragraph_1.text.strip()

        additional_blocks = article_bs.find('div', class_='l-col-center-590 article__content')
        inner_blocks_2 = additional_blocks.find_all('div', class_='article__text')
        for inner_block_2 in inner_blocks_2:
            paragraphs_2 = inner_block_2.find_all('p')
            for paragraph_2 in paragraphs_2:
                self.article.text += paragraph_2.text.strip()

    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self.article.save_raw()

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.removedirs(base_path)
    except FileNotFoundError:
        pass
    finally:
        os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    seed_urls = config['seed_urls']
    total_articles = config['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError
    for article_url in seed_urls:
        correct_url = re.match(r'https://', article_url)
        if not correct_url:
            raise IncorrectURLError

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError

    if total_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles


if __name__ == '__main__':
    seed_links, maximum_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls=seed_links, max_articles=maximum_articles)
    crawler.find_articles()
