"""
Scrapper implementation
"""
from pathlib import Path
import datetime
import json
import re
import shutil
import time
from bs4 import BeautifulSoup
import requests
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, ROOT_URL, HEADERS
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
        class_bs = article_bs.find('div', class_='view-content view-rows')
        title_bs = class_bs.find_all('td', class_="views-field views-field-title table__cell")
        for link_bs in title_bs:
            if len(self.urls) >= self.max_articles:
                break
            link_bs = link_bs.find('a')
            self.urls.append(ROOT_URL + link_bs['href'])


    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, HEADERS)
            time.sleep(1)
            article_bs = BeautifulSoup(response.text, 'html.parser')
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


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
    for seed_url in seed_urls:
        if not re.match(r'https?://', seed_url) or ROOT_URL not in seed_url:
            raise IncorrectURLError
    if not seed_urls:
        raise IncorrectURLError
    if not isinstance(seed_urls, list):
        raise IncorrectURLError
    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError
    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError
    if max_articles == 0 or max_articles < 0:
        raise IncorrectNumberOfArticlesError
    prepare_environment(ASSETS_PATH)
    return seed_urls, max_articles


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def parse(self):
        self.article = Article(self.article_url, self.article_id)
        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()
        return self.article

    def _fill_article_with_text(self, article_bs):
        table_rows_bs = article_bs.find('iframe', class_='pdf')
        url_of_pdf = table_rows_bs['data-src']
        pdf_raw_file = PDFRawFile(url_of_pdf, self.article_id)
        pdf_raw_file.download()
        self.article.text = pdf_raw_file.get_text()
        if 'Литература' in self.article.text:
            new_list = self.article.text.split('Литература')
            new_list_without_literature = ''.join(new_list[:-1])
            self.article.text = new_list_without_literature

    def _fill_article_with_meta_information(self, article_bs):
        author_bs = article_bs.find('span', class_='field__item-wrapper')
        author_bs = 'NOT FOUND' if not author_bs else author_bs.text
        title_of_the_article_bs = article_bs.find('title')
        title_of_the_article_bs = title_of_the_article_bs.text
        data_bs = article_bs.find('div', class_='node__content clearfix')
        data = data_bs.find('div',
                            {'style':'text-align: left; font-weight: bold; margin-bottom: 10px;'})
        full_data_string = data.text
        data_year_string = re.search(r'\s+\d{4}', full_data_string)
        data_year = data_year_string.group(0)[-4:]
        volume_number = re.search(r'-\d/', self.article_url).group(0)[1]
        date = datetime.datetime(int(data_year), 6 * int(volume_number), 1)
        self.article.author = author_bs
        self.article.title = title_of_the_article_bs
        self.article.date = date


if __name__ == '__main__':
    another_seed_urls, total_articles = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(another_seed_urls, total_articles)
    crawler.find_articles()
    for identifier, url in enumerate(crawler.urls):
        number = HTMLParser(url, identifier + 1)
        article = number.parse()
