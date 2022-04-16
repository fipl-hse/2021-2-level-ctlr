"""
Scrapper implementation
"""
import datetime
import json
import random
import re
import shutil
from collections import namedtuple
from pathlib import Path
from time import sleep
from typing import List

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from constants import HEADERS, CRAWLER_CONFIG_PATH, ASSETS_PATH, ISSUE_YEARS, ISSUE_MONTHS
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
    Total number of articles to parse is not integer  # in|is !typo
    """


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls: List[str], max_articles: int):
        self.seed_urls = seed_urls
        self.total_max_articles = max_articles
        self.urls = []

    @staticmethod
    def _extract_url(article_bs):
        contents_bs = article_bs.select('div.content-cont-col-text a')
        links = ['https://alp.iling.spb.ru/' + content['href'][2:] for content in contents_bs if not 'static' in content['href']]
        return links

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            page = obtain_page(url)
            if page:
                soup = BeautifulSoup(page, 'lxml')
                seed_pages = self._extract_url(soup)[:self.total_max_articles - len(self.urls)]
                self.urls.extend(seed_pages)
                if len(self.urls) == self.total_max_articles:
                    return

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class CrawlerRecursive(Crawler):
    """
    Recursive Crawler
    """
    def find_articles(self):
        try:
            seed, self.seed_urls = self.get_search_urls()
            for next_seed in self.seed_urls:
                page = obtain_page(next_seed)
                if page:
                    soup = BeautifulSoup(page, 'lxml')
                    seed_pages = self._extract_url(soup)[:self.total_max_articles - len(self.urls)]
                    self.urls.extend(seed_pages)
                    if len(self.urls) == self.total_max_articles:
                        return
        except TypeError:
            return

    def get_search_urls(self):
        seed = self.seed_urls[0]
        page = obtain_page(seed)
        if page:
            soup = BeautifulSoup(page, 'lxml')
            next_pages = soup.select('div.archive-tom-one a')
            links_to_follow = ['https://alp.iling.spb.ru/' + next_page['href'] for next_page in next_pages if not next_page['href'].endswith('.pdf')]
            return seed, links_to_follow


class HTMLParser:
    """
    Parser implementation
    """

    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_bs):
        pdf_url = 'https://alp.iling.spb.ru/' + article_bs.select_one('div.article-download-r a')['href'][5:]
        pdf_file = PDFRawFile(pdf_url, self.article_id)
        pdf_file.download()
        self.article.text = pdf_file.get_text()

    def _fill_article_with_meta_information(self, article_bs):
        self.article.title = article_bs.select_one('h1.article-h1').text

        author = article_bs.select_one('span.author-name').text.replace('\n', ' ')
        if not author:
            self.article.author = 'NOT FOUND'
        self.article.author = author

        issue = re.search(r'(?P<volume>x.+)(?P<part>\d)(?=/)', self.article_url)
        date_raw = f"01.{ISSUE_MONTHS.get(issue.group('part'))}.{ISSUE_YEARS.get(issue.group('volume'))}"
        article_date = datetime.datetime.strptime(date_raw, '%d.%m.%Y')
        self.article.date = article_date

        self.article.topics = article_bs.select_one('div.kw-tags').text.split(', ')

    def parse(self):
        page = obtain_page(self.article_url)
        article_bs = BeautifulSoup(page, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def obtain_page(url):
    """
    Reaches seed url and returns its content
    """
    try:
        response = requests.get(url, headers=HEADERS)
        sleep(random.uniform(2, 4))
        response.encoding = 'UTF-8'
        return response.text
    except RequestException:
        return


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    shutil.rmtree(base_path, ignore_errors=True)
    Path(base_path).mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    n_articles = config.get('total_articles_to_find_and_parse')
    is_n_articles = isinstance(n_articles, int) and n_articles > 0
    is_n_in_range = is_n_articles and n_articles < 1000

    seed_urls = config.get("seed_urls")
    pattern = re.compile(r'https://alp\.iling\.spb\.ru/issues')
    is_seed_urls = seed_urls and all(pattern.match(str(seed)) for seed in seed_urls)

    Validation = namedtuple('Validation', ['success', 'error'])
    validations = (
        Validation(is_n_articles, IncorrectNumberOfArticlesError),
        Validation(is_n_in_range, NumberOfArticlesOutOfRangeError),
        Validation(is_seed_urls, IncorrectURLError),
    )

    for test in validations:
        if not test.success:
            raise test.error()

    return seed_urls, n_articles


if __name__ == '__main__':
    start_urls, max_n_articles = validate_config(CRAWLER_CONFIG_PATH)

    crawler = CrawlerRecursive(
        seed_urls=start_urls,
        max_articles=max_n_articles,
    )

    prepare_environment(ASSETS_PATH)

    crawler.find_articles()

    for index, article_link in enumerate(crawler.urls, start=1):
        parser = HTMLParser(article_url=article_link, article_id=index)
        article_instance = parser.parse()
        article_instance.save_raw()
        print(f'Article #{index} is successfully loaded')
