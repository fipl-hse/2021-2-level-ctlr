# PDF Files Crawling Essentials

This documented is useful for those students who 
work with PDF articles. The document provides overview
of the key differences in PDF processing in comparison 
to HTML articles processing.

> **Note:** functions and parameters descriptions are the same as for HTMl processing.
> Read the [scrapper documentation](scrapper.md) for general descriptions and concepts.

## Terms

1. A *hybrid PDF* is a PDF file that contains only one article
   (see [example page](https://vja.ruslang.ru/ru/archive/2021-3) with hybrid PDF).
2. A *monolithic PDF* is a PDF file that contains several articles inside it 
   (see [example page](https://vestnik.philol.msu.ru) with monolithic PDF).

> **Note:** The implementation for these two types of PDF files processing is different.

## Hybrid PDF Processing (mark 8 only if condition is met)

To crawl a hybrid PDF file, you need to implement the following crawler abstraction:

```python
class PDFCrawler(Crawler):
    pass
```

> **Note:** The `PDFCrawler` class should return links to HTML pages 
> where hybrid PDF files and their metadata are located.

To parse a page with a PDF file, you need to implement the following parser abstraction:

```python
class HTMLParser:
    pass
```

> **HINTS:** 
> * use the `PDFRawFile` class from the `pdf_utils` module to download a PDF file and get its text.
> * extract metadata from the HTML page where a hybrid PDF article is located.
> * fill the `Article` class instance with text and metadata extracted.

## Monolithic PDF Processing (mark 10 only if condition is met)

To crawl a monolithic PDF file, you need to implement the following crawler abstraction:

```python
class PDFCrawler(Crawler):
    pass
```

> **Note:** The `PDFCrawler` class should return links to monolithic PDF files 
> directly. Such links should end with `.pdf` extension.

To parse a monolithic PDF file, you need to implement the following parser abstraction:

```python
class PDFParser(HTMLParser):
    pass
```

> **HINTS:** 
> * introduce the algorithm to split a monolithic PDF file into several articles.
> * extract metadata from a monolithic PDF file directly for each article split.
> * extract text from a monolithic PDF file directly for each article split.
> * fill the `Article` class instance for each text and metadata extracted.

## Hybrid and Monolithic PDF Processing (mark 10 only if condition is met)

Some sources may contain both hybrid and monolithic PDF files.
In this case, the `PDFCrawler` class should be able to crawl
links of both types: hybrid and monolithic.

Both parsers `HTMLParser` and `PDFParser` should be implemented.
The call of parser class should depend on the type of the URL that is crawled by the `PDFCrawler`.
For URLs with the `.pdf` extension (monolithic PDF URLs), 
the `PDFParser` class implementation should be called.
