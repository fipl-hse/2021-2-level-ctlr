"""
Scrapper implementation
"""
from datetime import datetime
from pathlib import Path
import json
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
    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.urls = []


    def _extract_url(self, article_bs):
        not_full_urls = []
        all_urls_bs = article_bs.find_all('a')
        for url_bs in all_urls_bs:
            url_to_article = url_bs['href']
            not_full_urls.append(url_to_article)
        full_urls = [HTTP_PATTERN + not_full_url for not_full_url in
                     not_full_urls if not 'http' in not_full_url]

        for full_url in full_urls:
            if len(self.urls) < self.max_articles and full_url not in self.urls:
                self.urls.append(full_url)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep (3)
            response = requests.get(url=seed_url, timeout=60)
            if not response.ok:
                continue
            soup = BeautifulSoup (response.text, 'lxml')
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
        author_p_tag = article_bs.find(
            lambda tag: tag.name == "p" and 'strong' in tag.text)
        try:
            self.article.author = author_p_tag.find_all('sup')[1].text
        except (AttributeError, IndexError):
            try:
                author_span_tag = article_bs.find(
                    'span', class_='article-info__authors')
                self.article.author = author_span_tag.find_all('span')[1].text
            except (AttributeError, IndexError):
                self.article.author = 'NOT FOUND'
                #KEY_WORDS
        self.article.topics = 'NOT FOUND'

        try:
            raw_date = article_bs.find_all('span',
                                           class_='article-info__data')[1].text
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
            self.article.date = datetime.datetime.strptime(raw_date,'%d %m %Y')
        except (ValueError, IndexError):
            self.article.date = datetime.datetime.today()
        self.article.title = article_bs.find("meta", property="og:title")[
            'content']

    def _fill_article_with_text(self, article_bs):
        text = article_bs.find('p').text
        self.article.text = text

    def parse(self):
        response = requests.get(url=self.article_url)
        if response.status_code == 200:

            article_bs = BeautifulSoup(response.text, 'lxml')

            self._fill_article_with_text(article_bs)
            self._fill_article_with_meta_information(article_bs)
        else:
            self.article.title = 'NOT FOUND'
            self.article.date = datetime.datetime.today()
            self.article.author = 'NOT FOUND'
            self.article.topics = []
            self.article.text = 'NOT FOUND'
        return self.article



def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    main_path = Path(base_path)
    if main_path.exists():
        shutil.rmtree(base_path)
    main_path.mkdir(parents = True)

def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration = json.load(file)

    if not configuration ['seed_urls']:
        raise IncorrectURLError

    for url in configuration["seed_urls"]:
        if HTTP_PATTERN not in url:
            raise IncorrectURLError

    seed_urls = configuration["seed_urls"]
    total_articles_to_find_and_parse = configuration["total_articles_to_find_and_parse"]

    if not isinstance(total_articles_to_find_and_parse, int) or total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles_to_find_and_parse


if __name__ == '__main__':
    seed_urls_main, total_articles_main = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(seed_urls_main, total_articles_main)
    crawler.find_articles()

    COUNTER_ID = 1
    for article_url_main in crawler.urls:
        article_parser = HTMLParser(article_url = article_url_main, article_id = COUNTER_ID)
        article = article_parser.parse()
        article.save_raw()
        COUNTER_ID += 1
