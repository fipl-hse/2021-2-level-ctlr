"""
Scrapper implementation
"""
from datetime import datetime
from pathlib import Path
import random
import re
import shutil
import time
import json

from bs4 import BeautifulSoup
import requests
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

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
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        link = article_bs.find('a')
        return 'https://www.m24.ru' + link['href']

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            if len(self.urls) >= self.max_articles:
                break

            response = requests.get(seed_url, headers=get_random_headers(), allow_redirects=True, timeout=5)
            time.sleep(2.0 + random.uniform(0.0, 2.0))
            with open('index1.html', 'w', encoding='utf-8') as file:
                file.write(response.text)

            article_bs = BeautifulSoup(response.text, 'html.parser')
            class_bs = article_bs.find('div', class_="b-materials-list b-list_infinity")
            title_bs = class_bs.find_all('p', class_="b-materials-list__title")

            for link_bs in title_bs:
                if len(self.urls) >= self.max_articles:
                    break

                extracted_url = self._extract_url(link_bs)

                if extracted_url not in self.urls:
                    self.urls.append(extracted_url)

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
        response = requests.get(self.article_url, headers=get_random_headers(), allow_redirects=True, timeout=5)
        time.sleep(1.0 + random.uniform(0.0, 1.0))

        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()

        return self.article

    def _fill_article_with_text(self, article_bs):
        material_body_bs = article_bs.find('div', class_='b-material-body')
        paragraphs_bs = material_body_bs.find_all('p', class_=None)

        text = ''

        for paragraph_bs in paragraphs_bs:
            text = ''.join([text, paragraph_bs.text])

        self.article.text = text

    def _fill_article_with_meta_information(self, article_bs):
        material_before_body = article_bs.find('div', class_='b-material-before-body')

        title_bs = material_before_body.find('h1')
        self.article.title = title_bs.text

        topic_bs = material_before_body.find('div', class_='b-material__rubrics').find('a')
        self.article.topics = [topic_bs.text]

        tags_bs = material_before_body.find('div', class_='b-material__tags')
        author = 'NOT FOUND'

        for tag_bs in tags_bs:
            match = re.match(r'[А-Я][а-я]+\s[А-Я][а-я]+', tag_bs.text)

            if match:
                author = tag_bs.text
                break

        self.article.author = author

        head_title_bs = article_bs.find('title')
        date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', head_title_bs.text)
        date_time_string = date_match.group(0)

        time_bs = material_before_body.find('p', class_='b-material__date')
        time_match = re.search(r'\d{2}:\d{2}', time_bs.text)
        date_time_string = ' '.join([date_time_string, time_match.group(0)])

        date_time = datetime.strptime(date_time_string, '%d.%m.%Y %H:%M')
        self.article.date = date_time


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = Path(base_path)
    if path.is_dir():
        shutil.rmtree(path)

    path.mkdir(parents=True, exist_ok=True)


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

        if max_articles > 100000:
            raise NumberOfArticlesOutOfRangeError
        # если статей для парсинга больше 100000

        if max_articles == 0 or max_articles < 0:
            raise IncorrectNumberOfArticlesError
        # если число статей, которое мы
        # передаем в scrapper_config.json не является integer

        for seed_url in seed_urls:
            if seed_url[0:8] != 'https://' and seed_url[0:7] != 'http://':
                raise IncorrectURLError
        # если протокол не соответствует стандратному паттерну

        prepare_environment(ASSETS_PATH)  # пока не починили тесты

        return seed_urls, max_articles
        # возвращает список urls и число статей


def get_random_headers():
    software_names = [SoftwareName.CHROME.value, SoftwareName.ANDROID.value, SoftwareName.SAFARI.value,
                      SoftwareName.FIREFOX.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value,
                         OperatingSystem.CHROMEOS.value]
    useragent_random = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    return {'user-agent': useragent_random.get_random_user_agent(),
            'accept': '*/*', 'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}


if __name__ == '__main__':
    seed_urls_run, max_articles_run = validate_config(crawler_path=CRAWLER_CONFIG_PATH)
    #  prepare_environment(base_path=ASSETS_PATH)
    crawler = Crawler(seed_urls=seed_urls_run, max_articles=max_articles_run)
    crawler.find_articles()
    #  test

    for i, url in enumerate(crawler.urls):
        parser = HTMLParser(url, i + 1)
        parser.parse()
        parser.article.save_raw()
