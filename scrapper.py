"""
Scrapper implementation
"""
import re
from datetime import datetime
import json
from pathlib import Path
import shutil
import re
from bs4 import BeautifulSoup
import requests
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         'like Gecko) Chrome/99.0.4844.74 Safari/537.36'}

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
        table_rows = article_bs.find('div', class_='sections').find_all('div', class_='title')
        for table_row in table_rows:
            if len(self.urls) >= self.total_max_articles:
                break
            link = table_row.find('a')
            self.urls.append(link['href'])


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
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def parse(self):
        response = requests.get(self.article_url, headers=headers)
        article_bs = BeautifulSoup(response.text, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):
        fulltext = article_bs.find('ul', class_='value galleys_links')
        page_link = fulltext.find('a')['href']
        response_pdf = requests.get(page_link, headers=headers)
        pdf_bs = BeautifulSoup(response_pdf.text, 'html.parser')
        container = pdf_bs.find('header', class_='header_view')
        download_link = container.find('a', class_='download')['href']
        pdf = PDFRawFile(download_link, self.article_id)
        pdf.download()
        self.article.text = pdf.get_text()

    def _fill_article_with_meta_information(self, article_bs):
        article_title = article_bs.find('h1', class_='page_title').text
        article_title = article_title.strip()
        self.article.title = article_title
        article_author = article_bs.find('ul', class_='item authors')
        article_author = article_author.find('span', class_='name')
        if not article_author:
            article_author = 'NOT FOUND'
        else:
            article_author = article_author.text
            article_author = article_author.strip()
        self.article.author = article_author
        article_date = article_bs.find('div', class_='item published').find('div', class_='value')
        article_date = re.search(r'\d{4}-\d{2}-\d{2}', article_date.text)
        article_date = datetime.strptime(article_date.group(0), '%Y-%m-%d')
        self.article.date = article_date

def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path_to_base_path = Path(base_path)
    try:
        shutil.rmtree(base_path)
    except FileNotFoundError:
        pass
    path_to_base_path.mkdir(parents=True)

def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        scrapper_config = json.load(file)

    seed_urls = scrapper_config["seed_urls"]
    max_articles = scrapper_config["total_articles_to_find_and_parse"]

    if 'total_articles_to_find_and_parse' not in scrapper_config:
        raise IncorrectNumberOfArticlesError

    if 'seed_urls' not in scrapper_config:
        raise IncorrectURLError

    if not seed_urls or not isinstance(seed_urls, list):
        raise IncorrectURLError

    for seed_url in seed_urls:
        if not isinstance(seed_url, str):
            raise IncorrectURLError

    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError

    if  max_articles == 0:
        raise IncorrectNumberOfArticlesError

    if not 0 < max_articles <= 100:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles

if __name__ == '__main__':
    # YOUR CODE HERE
    new_seed_urls, total_articles_to_find_and_parse = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(new_seed_urls, total_articles_to_find_and_parse)
    crawler.find_articles()
    for i, my_url in enumerate(crawler.urls):
        parser = HTMLParser(my_url, i + 1)
        article = parser.parse()
        article.save_raw()
