"""
Scrapper implementation
"""
import re
import json
from pathlib import Path
import shutil
import os
import requests
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
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
        urls = article_bs.find('div', class_='jscroll-inner')
        urls_to_aritcle = urls.find('a')

        new = []
        for article in urls_to_aritcle:
            urls_bs = article['href']
            pattern = r'https://vz.ru'
            need_url = re.search(r'https://', urls_bs)
            if not need_url:
                new.append(pattern + urls_bs)
            else:
                new.append(urls_bs)
        return new


    def find_articles(self):
        """
        Finds articles
        """
        url = 'https://vz.ru/news/'
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        try:
            for link in soup.find_all('a', attrs={'href': re.compile("^http[s]?://")}):
                print(link.get('href'))
        except KeyError:
            print('Incorrect link')

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

    def _fill_article_with_text(self, article_bs):
        text_bs = article_bs.find('div', class_='text')
        self.article.text = text_bs.text
        print(text_bs)


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
    path.mkdir(exist_ok=True, parents=True)

    # try:
    #    os.rmdir(base_path)  # removing directory
    #  except FileNotFoundError:
    #    pass
    # os.mkdir(base_path)  # creating directory


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']

    if not isinstance(seed_urls, list):
        raise IncorrectURLError

    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError

    for url in seed_urls:
        correct_url = re.match(r'https://', url)
        if not correct_url:
            raise IncorrectURLError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    if max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    return seed_urls, max_articles


if __name__ == '__main__':
    my_seed_urls, my_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(my_seed_urls, my_max_articles)
    crawler.find_articles()
