# `pdf_utils` module

The `pdf_utils` module exposes a class `PDFRawFile`that is 
used for PDF files handling. It is responsible for several aspects:

1. downloading PDF file by the given URL;
1. extracting the text of the downloaded PDF file.

This module is functional and given to you for further usage. Feel free to 
inspect its content. In case you think you have found a mistake, contact
assistant. Those who considerably improve this module will get additional 
bonuses.

> **HINT:** for `HTMLWithPDFParser` or `PDFParser` implementations, you need the following methods:
> * `PDFRawFile.__init__(...)`
> * `PDFRawFile.download(...)`
> * `PDFRawFile.get_text(...)`

> **NOTE**: `PDFRawFile` relies on `fitz` python library. 
> However, **do not install it directly!**
> Instead, install `PyMuPDF` library which contains all the necessary components
> for `PDFRawFile` to function correctly.
> Naturally, do not forget to list it in `requirements.txt`.
