"""
Scrapper implementation
"""
from datetime import datetime
import json
import re
import shutil
from random import randint
from time import sleep

import requests
from bs4 import BeautifulSoup
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
    def __init__(self, seed_urls, total_max_articles: int):
        self.seed_urls = seed_urls
        self.total_articles_to_find_and_parse = total_max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        articles_block = article_bs.find('div', class_='tnb_img clear')
        articles_bs = articles_block.find_all('p', recursive=False)
        urls = []
        for art_bs in articles_bs:
            urls.append('https://daily-nn.ru' + art_bs.find('a')['href'])
        return urls

    def find_articles(self):
        """
        Finds articles
        """
        for article_url in self.seed_urls:
            sleep(randint(1, 5))
            response = requests.get(article_url, timeout=60)
            if not response.ok:
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            s_urls = self._extract_url(soup)
            for url in s_urls:
                if len(self.urls) < self.total_articles_to_find_and_parse:
                    if url not in self.urls:
                        self.urls.append(url)

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
        title_bs = article_bs.find('div', class_='content_cn').find('h1')
        self.article.title = title_bs.text

        self.article.author = 'NOT FOUND'

        topics_bs = article_bs.find('div', class_='claer public_data').find('a')
        self.article.topics = topics_bs.text

        date_bs = article_bs.find('div', class_='claer public_data').find('span').text
        months = {"Января": "01", "Февраля": "02", "Марта": "03", "Апреля": "04",
                  "Мая": "05", "Июня": "06", "Июля": "07", "Августа": "08",
                  "Сентября": "09", "Октября": "10", "Ноября": "11",
                  "Декабря": "12"}
        for month in months:
            if month in date_bs:
                date_bs = date_bs.replace(month, months[month])
        self.article.date = datetime.strptime(date_bs, '\n%H:%M, %d %m %Y\n')

    def _fill_article_with_text(self, article_bs):
        # titles_bs = article_bs.find()
        # self.article.text = titles_bs.text
        # divs = article_bs.find('div', class_='content_cn')
        # ps = divs.find_all('p')
        # self.article.text = ''
        # for p in ps:
        #     self.article.text += p.text
        self.article.text = article_bs.find('div', class_='content_cn').text

    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r') as file:
        config = json.load(file)
    article_urls = config['seed_urls']
    if not isinstance(article_urls, list) or not article_urls:
        raise IncorrectURLError
    for article_url in article_urls:
        correct_url = re.match(r'https://', article_url)
        if not correct_url:
            raise IncorrectURLError
    total_articles = config['total_articles_to_find_and_parse']
    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError
    if total_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if total_articles > 200:
        raise NumberOfArticlesOutOfRangeError
    return article_urls, total_articles


if __name__ == '__main__':
    seed_urls_config, total_articles_config = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(seed_urls=seed_urls_config, total_max_articles=total_articles_config)
    crawler.find_articles()

    for id_article, crawler_url in enumerate(crawler.urls):
        parser = HTMLParser(article_url=crawler_url, article_id=id_article+1)
        article = parser.parse()
        article.save_raw()
