"""
Scrapper implementation
"""

import json
import re
import shutil

from bs4 import BeautifulSoup
import requests

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, ROOT_URL, HEADERS
from core_utils import pdf_utils
from core_utils.article import Article, date_from_meta


class IncorrectURLError(Exception):
    """
    Seed URL does not match standard pattern
    """
    pass


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Total number of articles to parse is too big
    """
    pass


class IncorrectNumberOfArticlesError(Exception):
    """
    Total number of articles to parse in not integer
    """
    pass


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        main_block_bs = article_bs.find('div', {'class': 'two_thirds'})
        urls_bs = main_block_bs.find_all('a')
        return urls_bs

    def find_articles(self):
        """
        Finds articles
        """
        articles_to_find = self.max_articles

        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=HEADERS)
            if not response.ok:
                print('request failed')

            soup = BeautifulSoup(response.text, 'lxml')
            urls_bs = self._extract_url(soup)

            for url_bs in urls_bs:
                if articles_to_find == 0:
                    break

                if 'http://journals.tsu.ru' + url_bs['href'] not in self.urls:
                    self.urls.append('http://journals.tsu.ru' + url_bs['href'])
                    articles_to_find -= 1

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class HTMLParser:
    def __init__(self, full_url, i):
        self.article_url = full_url
        self.article_id = i
        self.article = Article(self.article_url, self.article_id)

    def _fill_article_with_text(self, article_bs):
        pdf_link = article_bs.find('a', {'class': 'file pdf'})['href']
        article_instance = pdf_utils.PDFRawFile(pdf_link, self.article_id)
        article_instance.download()
        pdf_text = article_instance.get_text()
        main_text = pdf_text.split('Литература \n')[0]
        article_text = ''.join(main_text)
        self.article.text = article_text

    def _fill_article_with_meta_information(self, article_bs):
        main_body_bs = article_bs.find('div', {'class': 'two_thirds'})
        self.article.title = main_body_bs.find('h1').text

        authors_table_bs = main_body_bs.find('table', {'class': 'content_table otvet_list'})
        authors_table_raws_bs = authors_table_bs.find_all('tr')[1:]
        authors_list = []
        for table_raw in authors_table_raws_bs:
            authors_list.append(table_raw.find('td').text)
        self.article.author = ', '.join(authors_list)

        topics = article_bs.find('meta', {'name': 'keywords'})['content']
        self.article.topics = topics.split(', ')

    def parse(self):
        web_page = requests.get(self.article_url, headers=HEADERS)
        article_bs = BeautifulSoup(web_page.text, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as config:
        data = json.load(config)

    seed_urls = data["seed_urls"]
    max_articles = data["total_articles_to_find_and_parse"]

    if not isinstance(seed_urls, list):
        raise IncorrectURLError

    if not seed_urls:
        raise IncorrectURLError

    for url in seed_urls:
        url_validation = re.match(ROOT_URL, url)
        if not url_validation:
            raise IncorrectURLError

    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError

    if max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 300:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


if __name__ == '__main__':
    print('Validating config...')
    valid_seed_urls, number_of_articles = validate_config(CRAWLER_CONFIG_PATH)
    if valid_seed_urls and number_of_articles:
        print(f'Config is correct.\nURLs found: {valid_seed_urls};\t'
              f'Number of articles to parse: {number_of_articles}')
        print('Preparing environment...')
        prepare_environment(ASSETS_PATH)

        print('Creating a crawler instance...')
        crawler = Crawler(valid_seed_urls, number_of_articles)
        crawler.find_articles()

        print('Parsing...')
        for article_id, article_url in enumerate(crawler.urls):
            article_parser = HTMLParser(article_url, article_id + 1)
            article = article_parser.parse()
            article.save_raw()
            print(f'Article {article_parser.article_id} of {number_of_articles} is done.')
            if article_parser.article_id == number_of_articles:
                break

        print('DONE')
