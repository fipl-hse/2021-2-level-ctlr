import requests
response = requests.get("https://www.pnp.ru/news/")
response.encoding = 'utf-8'
with open('index.html', 'w', encoding='utf-16') as file:
    file.write(response.text)
print(response.status_code)