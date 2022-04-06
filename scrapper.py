"""
Scrapper implementation
"""
from datetime import datetime, timedelta
import json
import re
from pathlib import Path
import random
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

from core_utils.article import Article
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, HTTP_PATTERN


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

    def __init__(self, seed_urls, total_max_articles):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        articles_blocks = article_bs.find_all('div', class_='card-article__content')
        not_full_urls = []
        for article_block in articles_blocks:
            try:
                not_full_url = article_block.find_parent()['href']
                not_full_urls.append(not_full_url)
            except TypeError:
                continue

        for url in not_full_urls:
            if len(self.urls) < self.total_max_articles and url:
                full_url = HTTP_PATTERN + url
                self.urls.append(full_url)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(random.randint(1, 7))
            response = requests.get(url=seed_url)
            response.encoding = 'utf-8'
            if not response.ok:
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            self._extract_url(soup)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(self.article_url, self.article_id)

    def _fill_article_with_meta_information(self, article_bs):
        try:
            self.article.author = article_bs.find('div', class_='article-authors__info').text.strip()
        except AttributeError:
            self.article.author = 'NOT FOUND'
        if self.article.author == 'NOT FOUND':
            try:
                self.article.author = article_bs.find('div', class_='article-authors__author').text.strip()
            except AttributeError:
                self.article.author = 'NOT FOUND'

        self.article.topics = article_bs.find('span', class_='tags').text.strip().split(' /  ')

        raw_date = article_bs.find('time').text
        if 'часов' in raw_date or 'часа' in raw_date or 'час' in raw_date:
            hours = int(raw_date.split()[0])
            full_date = datetime.today() - timedelta(hours=hours)
            raw_date = datetime.strftime(full_date, '%d %m, %H:%M %Y')
            self.article.date = datetime.strptime(raw_date, '%d %m, %H:%M %Y')
        elif 'Час' in raw_date:
            full_date = datetime.today() - timedelta(hours=1)
            raw_date = datetime.strftime(full_date, '%d %m, %H:%M %Y')
            self.article.date = datetime.strptime(raw_date, '%d %m, %H:%M %Y')
        elif 'минут' in raw_date or 'минуты' in raw_date or 'минута' in raw_date:
            minutes = int(raw_date.split()[0])
            full_date = datetime.today() - timedelta(minutes=minutes)
            raw_date = datetime.strftime(full_date, '%d %m, %H:%M %Y')
            self.article.date = datetime.strptime(raw_date, '%d %m, %H:%M %Y')
        elif 'День' in raw_date:
            full_date = datetime.today() - timedelta(days=1)
            raw_date = datetime.strftime(full_date, '%d %m, %H:%M %Y')
            self.article.date = datetime.strptime(raw_date, '%d %m, %H:%M %Y')
        else:
            months_dict = {'января': '01',
                           'февраля': '02',
                           'марта': '03',
                           'апреля': '04',
                           'мая': '05',
                           'июня': '06',
                           'июля': '07',
                           'августа': '08',
                           'сентября': '09',
                           'октября': '10',
                           'ноября': '11',
                           'декабря': '12',
                           }
            for month in months_dict:
                if month in raw_date:
                    raw_date = raw_date.replace(month, months_dict[month])
            pattern_of_date = r'\d{4}'
            is_date = re.findall(pattern_of_date, raw_date)
            if is_date:
                self.article.date = datetime.strptime(raw_date, '%d %m %Y, %H:%M /')
            else:
                raw_date = raw_date.replace('/', '2022')
                self.article.date = datetime.strptime(raw_date, '%d %m, %H:%M %Y')

        self.article.title = article_bs.find('h1', class_='article-headline__title').text.strip()

    def _fill_article_with_text(self, article_bs):
        self.article.text = article_bs.find('div', class_='article-boxes-list article__boxes').text

    def parse(self):
        response = requests.get(url=self.article_url)
        response.encoding = 'utf-8'
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path_for_environment = Path(base_path)
    if path_for_environment.exists():
        shutil.rmtree(base_path)
    path_for_environment.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration = json.load(file)

    for url in configuration["seed_urls"]:
        if HTTP_PATTERN not in url:
            raise IncorrectURLError

    seed_urls = configuration["seed_urls"]
    total_articles_to_find_and_parse = configuration["total_articles_to_find_and_parse"]

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(total_articles_to_find_and_parse, int) or total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles_to_find_and_parse


if __name__ == '__main__':
    seed_urls_list, max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls_list, max_articles)
    crawler.find_articles()
    ID = 1
    for article_url_main in crawler.urls:
        article_parser = HTMLParser(article_url=article_url_main, article_id=ID)
        article = article_parser.parse()
        article.save_raw()
        ID += 1
