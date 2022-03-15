"""
Scrapper implementation
"""
import requests
from bs4 import BeautifulSoup
import re


def main():
    response = requests.get('https://vz.ru/')
    print(response.status_code)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(response.text)


main()


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
        url = 'https://vz.ru/news/'
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        try:
            for link in soup.find_all('a', attrs={'href': re.compile("^http[s]?://")}):
                print(link.get('href'))
        except KeyError:
            print('Incorrect link')

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
