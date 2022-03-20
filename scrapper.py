"""
Scrapper implementation
"""
import json
import os
import requests
import re
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from pathlib import Path

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
        self.max_articles = max_articles
        self.seed_urls = seed_urls
        self.count_articles = 0
        self.article_urls = []


    def _extract_url(self, article_bs): #I don't understand if I need to collect seed urls (from main to year)
        # or just put it in scrapper_config.
        articles_code_stored_here = article_bs.find('div', class_='articles')
        links_articles = articles_code_stored_here.find_all('a')
        for link in links_articles:
            try:
                art_link = link["href"]
                if art_link.startswith('/'):
                    self.article_urls.append('https://periodical.pstgu.ru' + link["href"])
            except KeyError:
                continue


    def find_articles(self):
        """
        Finds articles
        """ # I also don't understand what I need to do here, because this code can be moved to extract_url
        for seed_url in self.seed_urls:
            issue_page = requests.get(seed_url.text)
            issue_page_bs = BeautifulSoup(issue_page.text, 'html.parser')
            self._extract_url(issue_page_bs)


    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return seed_urls


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if os.path.isdir(base_path):
        if os.path.exists(base_path):
            os.rmdir(base_path)
            os.mkdir(base_path)
        else:
            os.mkdir(base_path)
    else:
        print('Incorrect path')



def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as path_thing_idk:
        config_dict = json.load(path_thing_idk)
    seed_urls = config_dict['seed_urls']
    max_articles = config_dict["total_articles_to_find_and_parse"]
    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if max_articles > 150:
        raise NumberOfArticlesOutOfRangeError
    if not isinstance(seed_urls, list):
        raise IncorrectURLError
    for seed_url in seed_urls:
        if not (isinstance(seed_url, str) or seed_url.startswith('https://')):
            raise IncorrectURLError
    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    seed_urls, max_articles = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(seed_urls, max_articles)
    pass
