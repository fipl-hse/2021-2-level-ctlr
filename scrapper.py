"""
Scrapper implementation
"""

import json
import os
import requests
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile
# import re


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}

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
        self.total_max_articles = max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        class_bs = article_bs.find('div', class_='container-fluid').find_all('li')
        for link_search_bs in class_bs:
            self.urls.append('http://www.vestnik.vsu.ru' + link_search_bs.find('a')['href'])


    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=headers)
            article_bs = BeautifulSoup(response.text, 'html.parser')
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls

class HTMLParser:
    def __init__(self, full_url, i):
        self.article_url = full_url
        self.article_id = i
        self.article = Article(full_url, i)

    def parse(self):
        article_bs = BeautifulSoup(requests.get(self.article_url, headers=headers).text, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()
        return self.article

    def _fill_article_with_text(self, article_bs):
        table_rows = article_bs.find_all('div', class_='container-fluid')
        for table_row in table_rows:
            table_data = table_row.find_all('a')
            for new_table_data in table_data:
                if "Текст (PDF)" in new_table_data:
                    url = new_table_data['href']
                    pdf_raw_file = PDFRawFile(url, self.article_id)
                    pdf_raw_file.download()
                    text = pdf_raw_file.get_text()
                    parts_of_article = text.split('ЛИТЕРАТУРА')
                    self.article.text = ''.join(parts_of_article[:-1])


    def _fill_article_with_meta_information(self, article_bs):
        self.article.author = article_bs.find('i').get_text()
        self.article.title = article_bs.find('b').get_text()


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.rmdir(ASSETS_PATH)
    except FileNotFoundError:
        os.mkdir(ASSETS_PATH)

def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        scrapper_config = json.load(file)

    seed_urls = scrapper_config["seed_urls"]
    max_articles = scrapper_config["total_articles_to_find_and_parse"]

    if not seed_urls or not isinstance(seed_urls, list):
        raise IncorrectURLError

    for seed_url in seed_urls:
        if not isinstance(seed_url, str):
            raise IncorrectURLError

    if not isinstance(max_articles, int) or (max_articles == 0):
        raise IncorrectNumberOfArticlesError

    if not 0 < max_articles <= 100:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles

if __name__ == '__main__':
    # YOUR CODE HERE
    another_seed_urls, total_articles = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(another_seed_urls, total_articles)
    print(crawler)
    #crawler.find_articles()
    #for identifier, url in enumerate(crawler.urls):
    #    number = HTMLParser(url, identifier + 1)
    #    article = number.parse()
    pass
