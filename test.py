import requests

html_file = requests.get('https://magadanpravda.ru/lenta-novostej/politics').text
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_file)