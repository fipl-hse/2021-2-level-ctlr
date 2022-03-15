"""
Scrapper implementation
"""
import json
import os

import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from constants import ASSETS_PATH
from constants import CRAWLER_CONFIG_PATH
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
        class_bs = article_bs.find('div', class_="b-materials-list b-list_infinity")
        title_bs = class_bs.find_all('p', class_="b-materials-list__title b-materials-list__title_news")
        for link in title_bs:
            link = link.find('a')
            self.urls.append('https://www.m24.ru' + link['href'])

    def find_articles(self):
        """
        Finds articles
        """
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        useragent_random = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        headers = {'user-agent': useragent_random.get_random_user_agent(),
                   'accept': '*/*', 'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}

        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=headers, allow_redirects=True, timeout=5)
            print(response.status_code)
            with open('index1.html', 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(response.status_code)
            article_bs = BeautifulSoup(response.text, 'html.parser')
            self._extract_url(article_bs)

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

    def parse(self):
        response = requests.get(self.article_url)
        # прописать обманку для сайта!!!
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()

        return self.article

    def _fill_article_with_text(self, article_bs):

    def _fill_article_with_meta_information(self, article_bs):


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.rmdir(base_path)
    except FileNotFoundError:
        pass
    os.mkdir(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
        seed_urls = config['seed_urls']
        max_articles = config['total_articles_to_find_and_parse']

        if not isinstance(seed_urls, list):
            raise IncorrectURLError
        # если переменная seed_urls не является списком

        if not seed_urls:
            raise IncorrectURLError
        # возбуждает исключение, если такого seed_url
        # нет в списке, который мы сделали в scrapper_config.json

        if not isinstance(max_articles, int):
            raise IncorrectNumberOfArticlesError
        # если число статей, которое мы
        # передаем в scrapper_config.json не является integer

        if max_articles > 100:
            raise NumberOfArticlesOutOfRangeError
        # если статей для парсинга больше 100

        if max_articles == 0 or max_articles < 0:
            raise IncorrectNumberOfArticlesError
        # если число статей, которое мы
        # передаем в scrapper_config.json не является integer

        for seed_url in seed_urls:
            if seed_url[0:8] != 'https://' and seed_url[0:7] != 'http://':
                raise IncorrectURLError
        # если протокол не соответствует стандратному паттерну

        return seed_urls, max_articles
        # возвращает список urls и число статей


if __name__ == '__main__':
    seed_urls, max_articles = validate_config(crawler_path=CRAWLER_CONFIG_PATH)
    prepare_environment(base_path=ASSETS_PATH)
    crawler = Crawler(seed_urls=seed_urls, max_articles=max_articles)
    crawler.find_articles()
    print(crawler.urls)
    # article.save_raw()


