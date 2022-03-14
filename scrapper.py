"""
Scrapper implementation
"""

impport re
import os

class IncorrectURLError(Exception):
    """
    Seed URL does not match standard pattern
    """
    #test


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
    if os.path.isdir(base_path):
        if not os.listdir(base_path):
            pass
        else:
            os.rmdir(base_path)
            os.mkdir(base_path)
    else:
        os.mkdir(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """

    with open(crawler_path) as file:
        config = json.load(file)

    urls = config["seed_urls"]
    articles = config["total_articles_to_find_and_parse"]
    http_regex = r'http[s]?://+'

    if not isinstance(articles, int):
        raise IncorrectNumberOfArticlesError

    if articles > 1000 or articles < 0:
        raise NumberOfArticlesOutOfRangeError

    for url in urls:
        check = http_regex.search(url)
        if not check:
            raise IncorrectURLError

    return seed_urls, total_articles

if __name__ == '__main__':
    # YOUR CODE HERE
    pass
