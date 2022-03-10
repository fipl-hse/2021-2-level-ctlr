import requests

try:
    html_file = requests.get('https://snob.ru/theme/545/').text
    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(html_file)
except NameError:
    print('Website does not exist')