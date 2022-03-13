"""
Scrapper implementation
"""

import requests, urllib.error
from bs4 import BeautifulSoup


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

    def _extract_url(self, article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """

        url = 'https://aif.ru/dosug'
        response = requests.get(url, headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "accept-encoding": "gzip, deflate, br", "accept-language": 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,fr;q=0.6',
            "cookie": "__ddg1=3z7ohwF248ukR81grhvj; CookieMessenger=; _ga=GA1.2.1866016929.1646422780; _ym_d=1646422780; _ym_uid=1620758162826342715; __ddgid=MhwOCqWUpVMS0HAn; subscription_popup_min_state=week_view1; subscription_popup_state=%7B%22key%22%3A%22week_view1%22%2C%22timeout%22%3A1647599958264%7D; __ddgmark=JrhVBqNQJzM3xeRX; __ddg5=T7GglOZhSXdoo9HS; aif_sid=b806513bc5db4b27668b98a5d3e86f74; _gid=GA1.2.1353469175.1647194832; _ym_isad=1; _ym_visorc=b; _gat_gtag_UA_3672159_1=1"},
                                allow_redirects=True)
        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(response.text)

        return response, url


    def get_search_urls(self, response, url):
        """
        Returns seed_urls param
        """

        soup = BeautifulSoup(response.text, 'html.parser')

        div_bs = soup.find('div', class_ ="content")
        print(div_bs.text)

        all_links = soup.find_all('a')
        print(len(all_links))

        seed_urls = []

        for link in all_links:
            try:
                # print(url + link['href'])
                seed_urls.append(link['href'])
            except (KeyError, urllib.error.URLError, urllib.error.HTTPError):
                print('Found incorrect link')

            for elements in seed_urls:
                if ('http://' and 'https://') not in elements:
                    seed_urls.remove(elements)
        return seed_urls


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
