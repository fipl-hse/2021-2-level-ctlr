"""
Scrapper implementation
"""
import datetime
import os
import json
import requests
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile
import re


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
            self.urls.append('https://rjano.ruslang.ru' + link_bs['href'])


    def find_articles(self):
        """
        Finds articles
        """
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers)
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
    if os.path.isdir(base_path):
        files = os.listdir(base_path)
        for file in files:
            os.remove(os.path.join(base_path,file))
    else:
        os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']
    for seed_url in seed_urls:
        if seed_url[0:8] != 'https://' and seed_url[0:7] != 'http://':
            raise IncorrectURLError
    if not seed_urls:
        raise IncorrectURLError
    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError
    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError
    if max_articles == 0 or max_articles < 0:
        raise IncorrectNumberOfArticlesError
    if not isinstance(seed_urls, list):
        raise IncorrectURLError
    prepare_environment(ASSETS_PATH)
    return seed_urls, max_articles


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def parse(self):
        self.article = Article(self.article_url, self.article_id)
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        response = requests.get(self.article_url, headers)
        article_bs = BeautifulSoup(response.text, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()
        return self.article

    def _fill_article_with_text(self, article_bs):
        table_rows = article_bs.find('iframe', class_='pdf')
        print(table_rows['data-src'])
        url_of_pdf = table_rows['data-src']
        pdf_raw_file = PDFRawFile(url_of_pdf, self.article_id)
        pdf_raw_file.download()
        self.article.text = pdf_raw_file.get_text()
        print(len(self.article.text))
        if 'Литература' in self.article.text:
            new_list = self.article.text.split('Литература')
            new_list_without_literature = new_list[:-1]
            new_list_without_literature = ''.join(new_list_without_literature)
            self.article.text = new_list_without_literature
        print(len(self.article.text))


    def _fill_article_with_meta_information(self, article_bs):
        author_bs = article_bs.find('span', class_='field__item-wrapper')
        # author_bs = author_bs.get_text()
        if not author_bs:
            author_bs = 'NOT FOUND'
        else:
            author_bs = author_bs.get_text()
        # title_of_the_article_bs = article_bs.find('span', class_='field field-name-title field-formatter-string field-type-string field-label-hidden')
        title_of_the_article_bs = article_bs.find('title')
        title_of_the_article_bs = title_of_the_article_bs.get_text()
        data_bs = article_bs.find('div', class_='node__content clearfix')
        data = data_bs.find('div', {'style':'text-align: left; font-weight: bold; margin-bottom: 10px;'})
        # for x in data:
        #     print(x)
        #     print('')
        x = data.get_text()
        y = re.search(r'\s+\d{4}', x)
        print(y)
        another_symbol = y.group(0)[-4:]
        date = datetime.datetime(int(another_symbol), 1, 1)
        self.article.author = author_bs
        self.article.title = title_of_the_article_bs
        self.article.date = date
        print(date)

        # print(author_bs)
        # print(title_of_the_article_bs)
        # print(number)




if __name__ == '__main__':
    seed_urls, max_articles = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(seed_urls, max_articles)
    crawler.find_articles()
    # parser = HTMLParser(crawler.urls[0], 0)
    # article = parser.parse()
    for identificator, url in enumerate(crawler.urls):
        number = HTMLParser(url, identificator + 1)
        article = number.parse()
    # print(identificator)
    # print(article.text)

