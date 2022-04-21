from datetime import datetime

import requests
from bs4 import BeautifulSoup

def time():
    date_raw = '2022-03-10T11:00:00'
    date_parsed = datetime.strptime(date_raw, '%Y-%m-%dT%H:%M:%S')
    print(date_parsed)

    print(datetime.now() - date_parsed)

    processed_date_str = datetime.strftime(date_parsed, '%d-%y')
    print(processed_date_str)

#time()

def rusdate():
    date_raw_russian = '5 фев 2022'
    months = {
        'янв': '01',
        'фев': '02',
        'мар': '03'
    }

    for month in months.keys():
        if month in date_raw_russian:
            date_raw_alnum = date_raw_russian.replace(month, months[month])

    date_alnum_parsed = datetime.strptime(date_raw_alnum, '%d %m %Y')
    print(date_alnum_parsed)

rusdate()

def main():
    # 1. datetime manual creation - rarely needed in web scrapping
    past_time = datetime(year=1999, month=8, day=5)
    just_now_time = datetime.now()

    delta = just_now_time - past_time
    print(f'Since that time has passed {delta.total_seconds()} seconds')

    # 2. datetime creation from string - most frequent and difficult
    response = requests.get('https://www.nn.ru/text/economics/2022/03/10/70497161/')

    soup = BeautifulSoup(response.text, 'lxml')

    header_bs = soup.find('div', id='record-header')

    time_bs = header_bs.find('time')

    date_str = time_bs['datetime']
    print(date_str)  # 2022-03-10T11:00:00

    # 2.1 the best option is to have numeric only date
    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
    print(date)

    # 2.2 Russian words inside date might require additional efforts
    time_link_bs = time_bs.find('a')

    date_str = time_link_bs.text

    print(date_str)  # 10 марта 2022, 11:00

    # Refer to official docs: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    date_str = '10 марта 2022, 11:00'
    months = {
        'января': 'January',
        'февраля': 'February',
        'марта': 'March'
    }
    for month in months:
        date_str = date_str.replace(month, months[month])

    date = datetime.strptime(date_str, '%d %B %Y, %H:%M')
    print(date)

    # 2.3 using locale is possible but discouraged, but even using it, you need to
    # process cases, for example Genitive
    import locale
    locale.setlocale(locale.LC_ALL, 'ru_RU')

    date_str = time_link_bs.text
    try:
        date = datetime.strptime(date_str, '%d %B %Y, %H:%M')
    except ValueError:
        print('No way of processing months in Genitive. Normalize names first.')

    months = {
        'января': 'январь',
        'февраля': 'февраль',
        'марта': 'март'
    }
    for month in months:
        date_str = date_str.replace(month, months[month])

    print(date_str)

    date = datetime.strptime(date_str, '%d %B %Y, %H:%M')
    print(date)

    # 3. sometimes you really need to construct date from chunks
    response = requests.get('https://www.hse.ru/news/edu/570285789.html')

    hse_soup = BeautifulSoup(response.text, 'lxml')

    day = hse_soup.find('div', class_='post-meta__day').text
    month = hse_soup.find('div', class_='post-meta__month').text
    year = hse_soup.find('div', class_='post-meta__year').text

    month_mapping = {
        'мар': 3
    }

    date = datetime(year=int(year), month=month_mapping[month], day=int(day))
    print(date)

    # 4. after the datetime object is constructed, we might want to print it
    # in a special format, or we need to write it to a file

    date_str = date.strftime('Year: %Y, Month: %m.')
    print(date_str)

    date_str = date.strftime('%Y-%m-%d %H:%M:%S')
    print(date_str)


#if __name__ == '__main__':
#    main()
