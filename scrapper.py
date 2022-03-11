"""
Scrapper implementation
"""
import requests
from bs4 import BeautifulSoup
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
        pass

    def _extract_url(self, article_bs):
        response = requests.get('https://lingngu.elpub.ru/jour')
        with open('index.HTML', 'w', encoding='utf-8') as file:
            file.write(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = soup.find_all('a', attrs={'href': re.compile("^http[s]?://")})
        for link in all_links:
            print(link.get('href'))
        pass

    def find_articles(self):
        """
        Finds articles
        """
        pass

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


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
