"""
Scrapper implementation
"""

import json
import re
import shutil
import datetime

import requests
from bs4 import BeautifulSoup

from constants import ASSETS_PATH, HEADERS
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
        pass

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)

            if not response.ok:
                break

            soup = BeautifulSoup(response.text, 'lxml')

            articles = soup.find('div', class_='entry-content')
            all_links = articles.find_all('a')[1:]
            link_pattern = re.compile(r'https?://vestnik\.lunn\.ru/')
            for link in all_links:
                try:
                    if re.match(link_pattern, link['href']):
                        self.urls.append(link['href'])
                    else:
                        self.urls.append('https://vestnik.lunn.ru/' + link['href'])
                except KeyError:
                    print('Found incorrect link')

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(url=article_url, article_id=article_id)

    def parse(self):
        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article

    def _fill_article_with_text(self, article_bs):
        download_pdf = article_bs.find('a', {'class': 'aligncenter download-button'})['href']

        pdf = PDFRawFile(download_pdf, self.article_id)

        pdf.download()
        self.article.text = pdf.get_text()

    def _fill_article_with_meta_information(self, article_bs):
        self.article.title = article_bs.find('h1', {'class': 'entry-title'})

        article_authors = article_bs.find('div', {'class': 'entry-content'}).find_all('p')[1]
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

    seed_urls = config["seed_urls"]
    max_articles = config["total_articles_to_find_and_parse"]

    for url in seed_urls:
        right_url = re.match(r'https?://vestnik\.lunn\.ru/arhiv-zhurnala/', url)
        if not right_url:
            raise IncorrectURLError

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    prepare_environment(ASSETS_PATH)

    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
