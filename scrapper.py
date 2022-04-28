"""
Scrapper implementation
"""

import json
import requests
import re
import shutil
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from core_utils.article import Article
from datetime import datetime



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
        urls_dict = []

        for url in self.seed_urls:
            response = requests.get(url)

        article_bs = BeautifulSoup(response.text, 'html.parser')

        content = article_bs.find('section', class_='article_list content_list_js')
        all_urls = content.find_all('a')
        for url_to_article in all_urls:
            url = url_to_article['href']
            site_url = r'https://aif.ru'
            correct_url = re.search(r'https://', url)
            if correct_url:
                urls_dict.append(url)
            else:
                urls_dict.append(site_url + url)


    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url)

        article_bs = BeautifulSoup(response.text, 'html.parser')

        all_links = article_bs.find_all('a')
        seed_urls = []

        for article in article_bs:
            if len(self.urls) < self.max_articles:
                self._extract_url(article)


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


    def _fill_article_with_text(self, article_bs):
        text_of_article_bs = article_bs.find('span')
        self.article.text = text_of_article_bs.text


    def _fill_article_with_meta_information(self, article_bs):
        self.article.title = article_bs.find('h1', itemprop="headline").text

        self.article.tag = article_bs.find("span", itemprop="keywords", class_="item-prop-span")
        self.article.topics = article_bs.find()

        date_raw = article_bs.find("time", itemprop="datePublished")
        date_parsed = datetime.strptime(date_raw, '%d-%m-%Y %H:%M')
        self.article.date = date_parsed

        try:
            self.article.author = article_bs.find('span', itemprop="name", class_="item-prop-span").text
        except AttributeError:
            self.article.author = 'NOT FOUND'


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

    try:
        shutil.rmtree(base_path)
    except FileNotFoundError:
        print('File does not exist')

    base_path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """

    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if not isinstance(seed_urls, list) or not seed_urls:
        raise IncorrectURLError

    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError

    for url in seed_urls:
        if url[0:7] != 'http://' and url[0:8] != 'https://':
            raise IncorrectURLError
    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE

    urls, maximum_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls=urls, max_articles=maximum_articles)
    crawler.find_articles()

    for index, link in enumerate(crawler.urls):
        parser = HTMLParser(link, index + 1)
        article = parser.parse()
        article.save_raw()
