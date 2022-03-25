"""
Scrapper implementation
"""
import datetime
import json
from pathlib import Path
import random
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
        link_bs = article_bs.find('a')
        return ROOT_URL + link_bs['href']

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, HEADERS)
            time.sleep(1 + random.uniform(0.0, 1.0))
            article_bs = BeautifulSoup(response.text, 'html.parser')
            class_bs = article_bs.find('div', class_='view-content view-rows')
            title_bs = class_bs.find_all('td', class_="views-field views-field-title table__cell")
            for link_bs in title_bs:
                if len(self.urls) >= self.max_articles:
                    break
                if link_bs.find('em').text:
                    self.urls.append(self._extract_url(link_bs))

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
    if path.exists():
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
    if 'seed_urls' not in config:
        raise IncorrectURLError
    if 'total_articles_to_find_and_parse' not in config:
        raise IncorrectNumberOfArticlesError
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
    if max_articles <= 0:
        raise IncorrectNumberOfArticlesError
    return seed_urls, max_articles


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def parse(self):
        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):
        table_rows_bs = article_bs.find('iframe', class_='pdf')
        url_of_pdf = table_rows_bs['data-src']
        pdf_raw_file = PDFRawFile(url_of_pdf, self.article_id)
        pdf_raw_file.download()
        self.article.text = pdf_raw_file.get_text()
        if 'Л и т е р а т у р а' in self.article.text:
            new_list = self.article.text.split('Л и т е р а т у р а')
            number_of_references = new_list[-1]
            references = re.findall(r'([а-я]|[А-Я])+.{1,2}\d{4}\s+—', number_of_references)
            len_of_references = len(references)
            print(len_of_references)
            self.article.text = ''.join(new_list[:-1])


    def _fill_article_with_meta_information(self, article_bs):
        author_bs = article_bs.find('span', class_='field__item-wrapper')
        author_bs = 'NOT FOUND' if not author_bs else author_bs.text
        title_of_the_article_bs = article_bs.find('title')
        title_of_the_article_bs = title_of_the_article_bs.text
        data_bs = article_bs.find('div', class_='node__content clearfix')
        data = data_bs.find_all('div', class_=None)
        full_data_string = data[2].text
        data_year_string = re.search(r'\s+\d{4}', full_data_string)
        data_year = data_year_string.group(0)[-4:]
        volume_number = re.search(r'-\d/', self.article_url).group(0)[1]
        date = datetime.datetime(int(data_year), 6 * int(volume_number), 1)
        topics_div_bs = article_bs.find('div', class_='field field-node-field-klyu '
                                                      'field-entity-reference-type-taxonomy-term '
                                                      'field-formatter-entity-reference-label field-name-field-klyu '
                                                      'field-type-entity-reference field-label-above')
        if topics_div_bs:
            article_topics_bs = topics_div_bs.find_all('a')
            list_with_article_topics = []
            for topic_bs in article_topics_bs:
                list_with_article_topics.append(topic_bs.text)
            self.article.topics = list_with_article_topics
        self.article.author = author_bs
        self.article.title = title_of_the_article_bs
        self.article.date = date


if __name__ == '__main__':
    another_seed_urls, total_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(another_seed_urls, total_articles)
    crawler.find_articles()
    for identifier, url in enumerate(crawler.urls):
        number = HTMLParser(url, identifier + 1)
        article = number.parse()
        article.save_raw()
