"""
Scrapper implementation
"""
import requests
import json
import re

class IncorrectURLError(Exception):
    """
    Seed URL does not match standard pattern
    """
    pass


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
    try:
        with open(crawler_path) as file:
            config = json.load(file)

        seed_url = config["seed_url"]
        max_articles = config["total_articles_to find_and_parse"]

        for url in seed_url:
            validation = re.match(r'https?://', url)
            if not validation:
                raise IncorrectURLError

        if not isinstance(max_articles, int):
            raise IncorrectNumberOfArticlesError
        if max_articles > 300:
            raise NumberOfArticlesOutOfRangeError
        prepare_environment(ASSETS_PATH)
        return seed_url, max_articles

    except IncorrectURLError:
        print('IncorrectURLError')
    except NumberOfArticlesOutOfRangeError:
        print('NumberOfArticlesOutOfRangeError')
    except IncorrectNumberOfArticlesError:
        print('IncorrectNumberOfArticlesError')

if __name__ == '__main__':
    # YOUR CODE HERE
    pass
