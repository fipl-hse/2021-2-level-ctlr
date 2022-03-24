"""
Scrapper implementation
"""

import json, requests, shutil, urllib.error
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

        class_bs = article_bs.find('div', class_="content")
        title_bs = class_bs.findall('div', class_="text_box")

        for links_bs in title_bs:
            if len(self.urls) < self.max_articles:
                break


    def find_articles(self):
        """
        Finds articles
        """

        response = requests.get(self.seed_urls)

        article_bs = BeautifulSoup(response.text, 'html.parser')

        all_links = article_bs.find_all('a')
        seed_urls = []

        for link in all_links:
            try:
                seed_urls.append(link['href'])
            except (KeyError, urllib.error.URLError, urllib.error.HTTPError):
                print('Found incorrect link')

            for elements in seed_urls:
                if ('http://' and 'https://') not in elements:
                    seed_urls.remove(elements)


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

    base_path.mkdir(parent=True)


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
    return max_articles, seed_urls


if __name__ == '__main__':
    # YOUR CODE HERE

    seed_urls_try, max_articles_try = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(seed_urls_try, max_articles_try)
    crawler.find_articles()
