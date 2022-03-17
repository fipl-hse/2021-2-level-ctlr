# Technical Track of Computer Tools for Linguistic Research (2021/2022)

As a part of a compulsory course 
[Computer Tools for Linguistic Research](https://www.hse.ru/en/edu/courses/494759476)
in [National Research University Higher School of Economics](https://www.hse.ru/).

This technical track is aimed at building basic skills for retrieving data from external
WWW resources and processing it for future linguistic research. The idea is to automatically 
obtain a dataset that has a certain structure and appropriate content, 
perform morphological analysis using various natural language processing (NLP) 
libraries. [Dataset requirements](./docs/dataset.md).

Instructors: 

* [Khomenko Anna Yurievna](https://www.hse.ru/org/persons/65858472) - linguistic track lecturer
* [Lyashevskaya Olga Nikolaevna](https://www.hse.ru/staff/olesar) - linguistic track lecturer
* [Demidovskij Alexander Vladimirovich](https://www.hse.ru/staff/demidovs#sci) - technical track lecturer
* [Uraev Dmitry Yurievich](https://www.hse.ru/org/persons/208529395) - technical track practice lecturer
* [Kazyulina Marina Sergeevna](https://t.me/poemgranate) - technical track assistant

## Project Timeline

1. **Scrapper**
   1. Short summary: Your code can automatically parse a media website you are going to choose, 
      save texts and its metadata in a proper format
   1. Deadline: *March 25th, 2022*
   1. Format: each student works in their own PR
   1. Dataset volume: 5-7 articles
   1. Design document: [./docs/scrapper.md](./docs/scrapper.md)
   1. Additional resources:
      1. List of media websites to select from: at the `Resources` section on this page
1. **Pipeline**
   1. Short summary: Your code can automatically process raw texts from previous step,
      make point-of-speech tagging and basic morphological analysis.
   1. Deadline: *April 29th, 2022*
   1. Format: each student works in their own PR
   1. Dataset volume: 5-7 articles
   1. Design document: [./docs/pipeline.md](./docs/pipeline.md)

## Lectures history

|Date|Lecture topic|Important links|
|:--:|:---|:---|
|21.02.2022|Exceptions: built-in and custom for error handling and information exchange|[Introduction tutorial](https://realpython.com/python-exceptions/)|
|25.02.2022|Programming assignment: main concept and implementation details|**N/A**|

## Technical solution

| Module | Description | Component | I need to know them, if I want to get at least |
|:---|:---|:---|:---|
| [requests](https://pypi.org/project/requests/) | module for downloading web pages | scrapper | 4 |
| [`BeautifulSoup4`](https://pypi.org/project/beautifulsoup4/) | module for finding information on web pages | scrapper | 4 |
| [`lxml`](https://pypi.org/project/lxml/) | module for parsing HTML as a structure | scrapper | 6 |
| [pymystem3](https://pypi.org/project/pymystem3/) | module for morphological analysis | pipeline | 6 |
| [pymorphy2](https://pypi.org/project/pymorphy2/) | module for morphological analysis | pipeline | 8 |
| [pandas](https://pypi.org/project/pandas/) | module for table data analysis | pipeline | 10 |

Software solution is built on top of three components:
1. [`scrapper.py`](./scrapper.py) - a module for finding articles from the given media, extracting text and
   dumping it to the file system. Students need to implement it.
1. [`pipeline.py`](./pipeline.py) - a module for processing text: point-of-speech tagging and 
   basic morphological analysis. Students need to implement it.
1. [`article.py`](core_utils/article.py) - a module for article abstraction to incapsulate low-level
   manipulations with the article
   
## Handing over your work

Order of handing over:

1. lab work is accepted for oral presentation.
2. a student has explained the work of the program and showed it in action.
3. a student has completed the min-task from a mentor that requires some slight code modifications.
4. a student receives a mark:
   1. that corresponds to the expected one, if all the steps above are completed and mentor is satisfied with 
      the answer;
   2. one point bigger than the expected one, if all the steps above are completed and mentor is very 
      satisfied with the answer;
   3. one point smaller than the expected one, if a lab is handed over one week later than the deadline and 
      criteria from 4.1 are satisfied;
   4. two points smaller than the expected one, if a lab is handed over more than one week later than 
      the deadline and criteria from 4.1 are satisfied.

> NOTE: a student might improve their mark for the lab, if they complete tasks of the next level after handing over
> the lab.

A lab work is accepted for oral presentation if all the criteria below are satisfied:

1. there is a Pull Request (PR) with a correctly formatted name:
   `Laboratory work #<NUMBER>, <SURNAME> <NAME> - <UNIVERSITY GROUP NAME>`. Example: `Laboratory work #1, Kuznetsova Valeriya - 19FPL1`.
2. has a filled file `target_score.txt` with an expected mark. Acceptable values: 4, 6, 8, 10.
3. has green status.
4. has a label `done`, set by mentor.
 
## Resources

1. Academic performance: [link](https://docs.google.com/spreadsheets/d/1Jbp0KjNu4Ox4EJdC-zc-Lr5bt8r7YOmcZIfTv1qiNmM/edit?usp=sharing) 
1. Media websites list: [link](https://docs.google.com/spreadsheets/d/1GUBSxwZwrIOotQGDYD0Om7NKY0oui8Wn/edit?usp=sharing&ouid=105662922636302712328&rtpof=true&sd=true)
1. Python programming course from previous semester: [link](https://github.com/fipl-hse/2021-2-level-labs)
1. Scrapping tutorials: [YouTube series (russian)](https://youtu.be/7hn1_t2ZtJQ)
