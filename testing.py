import requests

html_file = requests.get('https://snob.ru').text
with open('test.html', 'w', encoding='utf-8') as f:
    f.write(html_file)