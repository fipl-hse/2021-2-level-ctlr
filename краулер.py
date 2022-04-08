import sqlite3
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re

conn = sqlite3.connect("news.db")
cur = conn.cursor()

cur.execute(
    """
CREATE TABLE IF NOT EXISTS texts 
(id INTEGER PRIMARY KEY AUTOINCREMENT, news_id text, date text, title text, full_text text)
"""
)

cur.execute(
    """
CREATE TABLE IF NOT EXISTS languages 
(id int PRIMARY KEY, language text) 
"""
)

cur.execute(
    """
CREATE TABLE IF NOT EXISTS text_to_language 
(id INTEGER PRIMARY KEY AUTOINCREMENT, id_text int, id_language int) 
"""
)

conn.commit()


def parse_news_page_block(one_block):
    block = {}
    a = one_block.find("a")
    block["title"] = one_block.find("div", {"class": "field-title"}).text
    block["link"] = (
        one_block.find("div", {"class": "field-item"}).find("a").attrs["href"]
    )
    if "ХантыйскийМансийский" in one_block.find("ul", {"class": "tabss"}).text:
        block["language"] = ["Русский", "Хантыйский", "Мансийский"]
    else:
        block["language"] = [
            i for i in one_block.find("ul", {"class": "tabss"}).text.split("\n") if i
        ]
    return block


def parse_one_article(block):
    url_one = "https://khanty-yasang.ru" + block["link"]
    req = session.get(url_one, headers={"User-Agent": ua.random})
    page = req.text
    soup = BeautifulSoup(page, "html.parser")
    block["full_text"] = soup.find("div", {"class": "field-item even"}).text
    block["date"] = soup.find("div", {'class': 'data'}).text
    return block


regex_id = re.compile("/([0-9]*)")


def get_nth_page(page_number):
    url = f"https://khanty-yasang.ru/frontpage?page={page_number}.html"
    req = session.get(url, headers={"User-Agent": ua.random})
    page = req.text
    soup = BeautifulSoup(page, "html.parser")

    boxes = soup.find_all("div", {"class": "section"})

    blocks = []
    for n in boxes:
        try:
            blocks.append(parse_news_page_block(n))
        except Exception as e:
            print(e)

    result = []
    for b in blocks:
        if b["link"].startswith("/"):
            idx = regex_id.findall(b["link"])[1]
            if idx not in seen_news:
                try:
                    res = parse_one_article(b)
                    res["news_id"] = idx
                    result.append(res)
                except Exception as e:
                    print(e)
            else:
                print("Seen", b["link"])

    return result


ua = UserAgent(verify_ssl=False)
session = requests.session()
page_number = 0


def write_to_db(block):
    languages = []
    for language in block["language"]:
        if language not in db_languages:
            if db_languages.values():
                db_languages[language] = max(db_languages.values()) + 1
            else:
                db_languages[language] = 1
            cur.execute(
                "INSERT INTO languages VALUES (?, ?)", (len(db_languages), language)
            )
            conn.commit()
        languages.append(db_languages[language])

    cur.execute(
        """
        INSERT INTO texts 
            (news_id, date, title, full_text) 
            VALUES (?, ?, ?, ?)
        """,
        (block["news_id"], block["date"], block["title"], block["full_text"]),
    )

    cur.execute("SELECT id FROM texts WHERE news_id = ?", (block["news_id"],))
    text_id = cur.fetchone()[0]

    languages = [(text_id, t) for t in languages]

    cur.executemany(
        "INSERT INTO text_to_language (id_text, id_language) VALUES (?, ?)", languages
    )

    conn.commit()

    seen_news.add(block["news_id"])


cur.execute("SELECT language, id FROM languages")
db_languages = {}
for name, idx in cur.fetchall():
    db_languages[name] = idx

cur.execute("SELECT news_id FROM texts")
seen_news = set(i[0] for i in cur.fetchall())



def run_all(n_pages):
    for i in range(n_pages):
        blocks = get_nth_page(i)
        for block in blocks:
            write_to_db(block)

ua = UserAgent(verify_ssl=False)
session = requests.session()
page_number = 0

run_all(20)

cur.execute(
    """
SELECT count(text_to_language.id) as cnt, languages.language
    FROM text_to_language
        JOIN languages ON languages.id = text_to_language.id_language
            GROUP BY text_to_language.id_language
            ORDER BY cnt DESC
            LIMIT 10;
"""
)
cur.fetchall()
