"""
Scrapper implementation
"""
import json
import re
import shutil
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, HEADERS
from core_utils.article import Article



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
        links_bs = article_bs.find_all('div', class_="issueArticle flex")
        the_beginning = 'https://lingngu.elpub.ru/jour'
        for url_bs in links_bs:
            the_end = url_bs.find('a')['href']
            full_url = the_beginning + the_end
            if len(self.urls) < self.max_articles and full_url not in self.urls:
                self.urls.append(full_url)


    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=HEADERS)
            response.encoding = 'windows-1251'
            if not response.ok:
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            self._extract_url(soup)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls

class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_meta_information(self, article_bs):
        title = article_bs.find('h1')
        self.article.title = title.text

        sublink_bs = article_bs.find('div', class_='sublink')
        author_bs = sublink_bs.find('a')
        self.article.author = author_bs.text

    def _fill_article_with_text(self, article_bs):
        text_bs = article_bs.find('div', class_='text')
        self.article.text = ''
        for text in text_bs:
            self.article.text += text.text

    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_text(article_bs)

        return self.article

def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = Path(base_path)
    if path.exists():
        shutil.rmtree(base_path)
    path.mkdir(parents=True, exist_ok=True)

def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)
    max_articles = config["total_articles_to_find_and_parse"]
    seed_urls = config["seed_urls"]
    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(seed_urls, list):
        raise IncorrectURLError

    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError

    if max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    part_of_string = re.compile(r'^https?://')

    for url in seed_urls:
        if not part_of_string.search(url):
            raise IncorrectURLError
    return seed_urls, max_articles


if __name__ == '__main__':
    seed_urls_test, max_articles_test = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(seed_urls_test, max_articles_test)
    crawler.find_articles()

    ID = 0
    for article_url_text in crawler.urls:
        ID += 1
        article_parser = HTMLParser(article_url_text, ID)
        article = article_parser.parse()
        article.save_raw()
