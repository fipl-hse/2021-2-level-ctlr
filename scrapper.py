"""
Scrapper implementation
"""
from datetime import datetime
import json
import random
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

from core_utils.article import Article
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH

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
        self.total_max_articles = total_max_articles
        self.urls = []
        

    def _extract_url(self, article_bs):
        not_full_urls = []
        all_urls_bs = article_bs.find_all('a", class_='newszagolobok')
        for url_bs in all_url_bs:
            url_to_article = url_bs['href']
            not_full_urls.append(url_to_article)
        full_urls = [HTTP_PATTERN + not_full_url for not_full_url in
                     not_full_urls if not 'http' in not_full_url]
                                          
        for full_url in full_urls:
            if len(self.urls) < self.total_max_articles and full_url not in self.urls:
                self.urls.append(full_url)
                                       
    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep (2)                              
            response = request.get(url=seed_url, timeout=60)
            if not response.ok:
                continue
            soup = BeautifulSoup (response.text, 'lxml')
            self._extract_url(soup)
            
                                          
    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls
 
 class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(self.article_url, self.article_id)
   


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


def validate_config(crawler_path):
    """
    Validates given config
    """
    pass


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
