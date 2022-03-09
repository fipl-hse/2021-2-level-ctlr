import requests

html_file = requests.get('https://www.m24.ru/news/').text
with open('test.html', 'w', encoding='utf-8') as f:
    f.write(html_file)

# idk where i should write my code
# that is why i created this file
# btw my website doesn't work
