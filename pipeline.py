import requests

"""
Pipeline for text processing implementation
"""


class EmptyDirectoryError(Exception):
    """
    No data to process
    """


class InconsistentDatasetError(Exception):
    """
    Corrupt data: numeration is expected to start from 1 and to be continuous
    """


class MorphologicalToken:
    """
    Stores language params for each processed token
    """

    def __init__(self, original_word):
        pass

    def get_cleaned(self):
        """
        Returns lowercased original form of a token
        """
        pass

    def get_single_tagged(self):
        """
        Returns normalized lemma with MyStem tags
        """
        pass

    def get_multiple_tagged(self):
        """
        Returns normalized lemma with PyMorphy tags
        """
        pass


class CorpusManager:
    """
    Works with articles and stores them
    """

    def __init__(self, path_to_raw_txt_data: str):
        pass

    def _scan_dataset(self):
        """
        Register each dataset entry
        """
        pass

    def get_articles(self):
        """
        Returns storage params
        """
        pass


class TextProcessingPipeline:
    """
    Process articles from corpus manager
    """

    def __init__(self, corpus_manager: CorpusManager):
        pass

    def run(self):
        """
        Runs pipeline process scenario
        """
        pass

    def _process(self, raw_text: str):
        """
        Processes each token and creates MorphToken class instance
        """
        pass


def validate_dataset(path_to_validate):
    """
    Validates folder with assets
    """
    pass


def main():
    html = 'https://vestnik.lunn.ru/arhiv-zhurnala/2021-god/vypusk-56-iv-kvartal-2021-g/'
    response = requests.get(html, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit'
                                                         '/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'})
    page_code = response.text

    with open('page_code.html', 'w', encoding='utf-8') as file:
        file.write(page_code)


if __name__ == "__main__":
    main()
