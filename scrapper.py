"""
Scrapper implementation
"""
import os
import re
import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
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
        urls_bs = article_bs.find_all('a', class_="flatCard_link__RANjL")
        the_beginning = 'https://nauka.tass.ru/'
        urls_bs_full = []
        for url_bs in urls_bs:
            the_end = url_bs['href']
            urls_bs_full.append(f'{the_beginning}{the_end}')

        return urls_bs_full

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url)
            if not response.ok:
                continue

            soup = BeautifulSoup(response.text, 'lxml')
            article_urls = self._extract_url(soup)
            for article_url in article_urls:
                self.urls.append(article_url)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_bs):
        text_content = article_bs.find('div', class_="text-content")
        divs = text_content.find_all('div', class_="text-block")
        for div in divs:
            ps = div.find_all('p')
            for p in ps:
                self.article.text += p.text.strip()

    def parse(self):
        response = requests.get(self.article_url)

        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self.article.save_raw()
        return self.article

def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.removedirs(base_path)
    except FileNotFoundError:
        pass
    finally:
        os.makedirs(base_path, )


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration = json.load(file)

    seed_urls = configuration['seed_urls']
    max_articles = configuration['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    part_of_string = re.compile(r'^https?://')
    for seed_url in seed_urls:
        if not part_of_string.search(seed_url):
            raise IncorrectURLError

    return seed_urls, max_articles

if __name__ == '__main__':
    # YOUR CODE HERE
    pass
