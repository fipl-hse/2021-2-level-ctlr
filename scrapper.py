"""
Scrapper implementation
"""
import datetime
import json
import re
from pathlib import Path
import shutil
from random import randint
from time import sleep

import requests
from bs4 import BeautifulSoup

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, HTTP_PATTERN
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
        urls_bs = article_bs.find_all('td', class_='views-field views-field-title table__cell')
        full_urls = []
        for url_bs in urls_bs:
            url = url_bs.find('a')['href']
            full_urls.append(HTTP_PATTERN + url)
        for full_url in full_urls:
            if len(self.urls) >= 100:
                break
            self.urls.append(full_url)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(randint(1, 5))
            response = requests.get(seed_url)

            if not response.ok:
                continue

            seed_url_bs = BeautifulSoup(response.text, 'lxml')

            self._extract_url(seed_url_bs)

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

    def _fill_article_with_text(self, article_bs):
        pdf_url = article_bs.find('iframe', class_='pdf')['data-src']
        pdf = PDFRawFile(pdf_url, self.article_id)
        pdf.download()

        pdf_with_lit = pdf.get_text()
        pdf_without_lit = pdf_with_lit.split('Литература')[0]

        self.article.text = pdf_without_lit

    def _fill_article_with_meta_information(self, article_bs):
        self.article.author = article_bs.find('span', class_='field__item-wrapper').text

        self.article.title = article_bs.find('span', class_='field field-name-title field-formatter-string '
                                                            'field-type-string field-label-hidden').text

        node_content = article_bs.find('div', class_='node__content clearfix')
        year = node_content.find('div').find_next_siblings()[2].text.strip('\n').strip(' ')[:4]
        self.article.date = datetime.date(int(year), 1, 1)

        topics_bs = article_bs.find_all('span', class_='field__item-wrapper')[1:]
        self.article.topics = [topic.text for topic in topics_bs]

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
    path_to_base_path = Path(base_path)
    if path_to_base_path.exists():
        shutil.rmtree(base_path)
    path_to_base_path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration = json.load(file)

    http_pattern = re.compile(HTTP_PATTERN)
    for url in configuration["seed_urls"]:
        result = http_pattern.search(url)
        if not result:
            raise IncorrectURLError

    seed_urls = configuration["seed_urls"]
    total_articles_to_find_and_parse = configuration["total_articles_to_find_and_parse"]

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(total_articles_to_find_and_parse, int):
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles_to_find_and_parse


if __name__ == '__main__':
    main_seed_urls, main_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(main_seed_urls, main_max_articles)
    crawler.find_articles()

    ID_OF_ARTICLE = 1
    for main_article_url in crawler.urls:
        article_parser = HTMLParser(article_url=main_article_url, article_id=ID_OF_ARTICLE)
        article = article_parser.parse()
        article.save_raw()
        ID_OF_ARTICLE += 1
        print(f'The {ID_OF_ARTICLE} article is done!')
