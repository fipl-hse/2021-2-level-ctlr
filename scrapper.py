"""
Scrapper implementation
"""

import requests
import json

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
        pass

    def find_articles(self):
        """
        Finds articles
        """
        # get data from website
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}
        response = requests.get('http://www.vestnik.vsu.ru/content/lingvo/index_ru.asp', headers=headers)
        # print(response.status_code)

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
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
    with open(crawler_path, 'r', encoding='utf-8') as file:
        scrapper_config = json.load(file)

    seed_urls = scrapper_config["seed_urls"]
    total_articles = scrapper_config["total_articles_to_find_and_parse"]

    if not seed_urls:
        raise IncorrectURLError

    for seed_url in seed_urls:
        if not isinstance(seed_url, str):
            raise IncorrectURLError

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError

    if not 0 < total_articles <= 100:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles

if __name__ == '__main__':
    # YOUR CODE HERE
    pass
