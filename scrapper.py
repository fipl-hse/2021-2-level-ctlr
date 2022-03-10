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
        pass

    def _extract_url(self, article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        html = 'https://vestnik.lunn.ru/arhiv-zhurnala/2021-god/vypusk-56-iv-kvartal-2021-g/'
        response = requests.get(html, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit'
                                                             '/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'})
        page_code = response.text

        with open('page_code.html', 'w', encoding='utf-8') as file:
            file.write(page_code)

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


def main():
    html = 'https://vestnik.lunn.ru/arhiv-zhurnala/2021-god/vypusk-56-iv-kvartal-2021-g/'
    response = requests.get(html, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit'
                                                         '/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'})
    page_code = response.text

    with open('page_code.html', 'w', encoding='utf-8') as file:
        file.write(page_code)


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
