"""
Scrapper implementation
"""

import datetime
import json
import random
import re
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, DOMAIN_NAME, HEADERS
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
        articles = article_bs.find('div', {'class': 'entry-content'})
        all_links = articles.find_all('a')[1:]
        domain_for_match = re.findall(r'.*(:.*)', DOMAIN_NAME)[0]
        for link in all_links:
            if len(self.urls) < self.max_articles:
                if re.match(r'https?' + domain_for_match, link['href']):
                    self.urls.append(link['href'])
                else:
                    self.urls.append(DOMAIN_NAME + link['href'])

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            sleep(random.randrange(2, 5))

            if not response.ok:
                continue

            article_bs = BeautifulSoup(response.text, 'lxml')

            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(url=article_url, article_id=article_id)

    def parse(self):
        response = requests.get(self.article_url, HEADERS)
        sleep(random.randrange(2, 5))

        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article

    def _fill_article_with_text(self, article_bs):
        download_pdf = article_bs.find('a', {'class': 'aligncenter download-button'})['href']

        pdf = PDFRawFile(download_pdf, self.article_id)

        pdf.download()
        full_article = pdf.get_text()

        reference = 'Список литературы / References'
        if reference in full_article:
            split_article = full_article.split(reference)
            self.article.text = ''.join(split_article[:-1])
        else:
            self.article.text = full_article

    def _fill_article_with_meta_information(self, article_bs):
        self.article.title = article_bs.find('h1', {'class': 'entry-title'}).text

        article_authors = article_bs.find('div', {'class': 'entry-content'}).find_all('p')[1].text
        if ',' in article_authors:
            self.article.author = article_authors.split(', ')[0]
        else:
            self.article.author = article_authors

        quarter_dict = {
            'I квартал': '01-01',
            'II квартал': '01-04',
            'III квартал': '01-07',
            'IV квартал': '01-10'
        }
        article_issue = article_bs.find_all('a', {'rel': 'v:url'})[3].text
        date_raw = article_issue[article_issue.find("(") + 1:article_issue.find(")")]
        for quarter in quarter_dict:
            if quarter in date_raw:
                dm_date = date_raw.replace(quarter, quarter_dict[quarter])

        self.article.date = datetime.datetime.strptime(dm_date, '%d-%m %Y г')

        article_topics = article_bs.find('tbody').find_all('tr')[3].find_all('td')[1].text
        self.article.topics = article_topics.replace('.', '').split('; ')


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir(exist_ok=True, parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    if "seed_urls" not in config:
        raise IncorrectURLError
    if "total_articles_to_find_and_parse" not in config:
        raise IncorrectNumberOfArticlesError

    seed_urls = config["seed_urls"]
    max_articles = config["total_articles_to_find_and_parse"]

    for url in seed_urls:
        right_url = re.match(DOMAIN_NAME, url)
        if not right_url:
            raise IncorrectURLError

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


if __name__ == '__main__':
    test_seed_urls, total_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(test_seed_urls, total_articles)
    crawler.find_articles()

    for i, test_url in enumerate(crawler.urls):
        parser = HTMLParser(test_url, i + 1)
        article = parser.parse()
        article.save_raw()
