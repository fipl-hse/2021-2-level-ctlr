"""
Scrapper implementation
"""
import requests


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
        pass

    def _extract_url(self, article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        counter = 1
        for i in self.seed_urls:

            response = requests.get(i)

            data = requests.get(i, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                                  'AppleWebKit/537.36 '
                                                                  '(KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'})
            with open(f'index{counter}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
                counter += 1


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

    pass
