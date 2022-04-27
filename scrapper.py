"""
Scrapper implementation
"""
from datetime import datetime
import json
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
        urls_bs = article_bs.find_all('div', class_='title')
        fulls = []
        for url_bs in urls_bs:
            part_of_url = url_bs.find('a')['href']
            if 'entry' in part_of_url:
                fulls.append(HTTP_PATTERN + part_of_url)

        for full in fulls:
            if len(self.urls) < self.total_max_articles and full not in self.urls:
                self.urls.append(full)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(random.randint(1, 8))
            response = requests.get(seed_url)
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
        self.article = Article(self.article_url, self.article_id)

    def _fill_article_with_meta_information(self, article_bs):
        # TITLE
        self.article.title = article_bs.find('div', class_='entry__title').find('h1').text.strip()
        # AUTHOR
        try:
            self.article.author = article_bs.find('span', class_='entry__author').text.strip()
        except AttributeError:
            self.article.author = "NOT FOUND"
        # DATE
        raw_date = article_bs.find('div', class_='time').text
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
            elif month.capitalize() in raw_date:
                raw_date = raw_date.replace(month.capitalize(), months_dict[month])
        self.article.date = datetime.strptime(raw_date, '%d %m %Y %H:%M')
        # TOPICS
        topics_bs = article_bs.find('div', class_='entry__tags').find_all('a')
        for topic_bs in topics_bs:
            self.article.topics.append(topic_bs.text[1:])

    def _fill_article_with_text(self, article_bs):
        text_of_article = ''
        texts = article_bs.find('article', class_='entry__body').find_all('p')
        for text_part in texts:
            text_of_article += text_part.text
        self.article.text = text_of_article

    def parse(self):
        response = requests.get(url=self.article_url)
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
        shutil.rmtree(path)
    path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    if not isinstance(config["seed_urls"], list):
        raise IncorrectURLError

    for url in config["seed_urls"]:
        if HTTP_PATTERN not in url:
            raise IncorrectURLError

    seed_urls = config["seed_urls"]
    max_articles = config["total_articles_to_find_and_parse"]

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


if __name__ == '__main__':
    test_seed_urls, test_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    print('craw')
    crawler = Crawler(test_seed_urls, test_max_articles)
    crawler.find_articles()

    print('pars')
    for id_of_article, article_url_test in enumerate(crawler.urls):
        id_of_article = id_of_article + 1
        article_parser = HTMLParser(article_url=article_url_test, article_id=id_of_article)
        article = article_parser.parse()
        article.save_raw()
        print(id_of_article,'done')
