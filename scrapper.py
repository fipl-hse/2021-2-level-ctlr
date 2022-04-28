"""
Scrapper implementation
"""
import datetime
import json
from pathlib import Path
import random
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

from core_utils.article import Article
from constants import HTTP_PATTERN, ASSETS_PATH, CRAWLER_CONFIG_PATH, HEADERS


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
        not_full_urls = []
        all_urls_bs = article_bs.find_all('a', class_='post-pre')
        for url_bs in all_urls_bs:
            url_to_article = url_bs['href']
            not_full_urls.append(url_to_article)
        full_urls = [HTTP_PATTERN + not_full_url for not_full_url in not_full_urls]

        for full_url in full_urls:
            if len(self.urls) < self.total_max_articles and full_url not in self.urls:
                self.urls.append(full_url)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(random.randint(1, 5))
            response = requests.get(url=seed_url, headers=HEADERS)
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
        self.article.author = 'NOT FOUND'

        try:
            post_tags = article_bs.find('div', class_='post-tags')
            topics_bs = post_tags.find_all('a', class_='post-tags__tag')
            self.article.topics = [topic_bs.text for topic_bs in topics_bs]
        except AttributeError:
            self.article.topics = 'NOT FOUND'

        raw_date = article_bs.find('div', class_='post-date').text
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
        self.article.date = datetime.datetime.strptime(raw_date, '%d %m %Y, %H:%M')

        self.article.title = article_bs.find('h1').text

        all_post_list_urls_bs = article_bs.find_all('a', class_='post-pre')
        print(all_post_list_urls_bs)


    def _fill_article_with_text(self, article_bs):
        text = article_bs.find('div', class_='post-text').text
        self.article.text = text

    def parse(self):
        response = requests.get(url=self.article_url,headers=HEADERS)

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

    if not configuration['seed_urls']:
        raise IncorrectURLError

    http_pattern = 'https://m.polit.ru'
    for url in configuration["seed_urls"]:
        if http_pattern not in url:
            raise IncorrectURLError

    seed_urls = configuration["seed_urls"]
    total_articles_to_find_and_parse = configuration["total_articles_to_find_and_parse"]

    if not isinstance(total_articles_to_find_and_parse, int):
        raise IncorrectNumberOfArticlesError
    if total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles_to_find_and_parse


if __name__ == '__main__':
    seed_urls_main, total_articles_main = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(seed_urls_main, total_articles_main)
    crawler.find_articles()

    ID = 1
    for article_url_main in crawler.urls:
        article_parser = HTMLParser(article_url=article_url_main, article_id=ID)
        article = article_parser.parse()
        article.save_raw()
        ID += 1
