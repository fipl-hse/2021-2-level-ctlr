"""
PDF files downloader implementation
"""

import os
import wget
import fitz

from constants import ASSETS_PATH


class PDFRawFile:
    """
    PDF files downloader class implementation.
    Knows how to download PDF from a given URL.
    Manages PDF's text.
    """

    def __init__(self, journal_url: str, journal_id: int):
        self._url = journal_url
        self._id = journal_id
        self.text = None

    def download(self):
        """
        Downloads PDF file by the URL given.
        """
        wget.download(self._url, os.path.join(ASSETS_PATH, f"{self._id}_raw.pdf"))

    def get_text(self):
        """
        Gets text from the PDF file downloaded.
        """
        text = ""
        # pylint: disable=E1101
        with fitz.open(os.path.join(ASSETS_PATH, f"{self._id}_raw.pdf")) as pdf:
            for page in pdf:
                text += page.get_text()
        return text

    @property
    def own_id(self):
        return self._id
