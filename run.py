import glob
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

session = requests.Session()


def login():
    datas = {
        'username': 'user',
        'password': 'user12345'
    }

    res = session.post('http://localhost:5000/login', data=datas)

    soup = BeautifulSoup(res.text, 'html5lib')

    page_item = soup.find_all('li', attrs={'class': 'page-item'})
    total_pages = len(page_item) - 2

    return total_pages


def get_urls(page):
    print('getting urls..... page {}'.format(page))

    res = session.get('http://localhost:5000', params={'page': page})

    soup = BeautifulSoup(res.text, 'html5lib')

    titles = soup.find_all(attrs={'class': 'card-title'})
    urls = []
    for title in titles:
        url = title.find('a')['href']
        urls.append(url)

    return urls


def get_detail(url):
    print('getting detail.....')

    res = session.get('http://localhost:5000' + url)

    soup = BeautifulSoup(res.text, 'html5lib')
    title = soup.find(attrs={'class': 'card-title'}).text.strip()
    price = soup.find(attrs={'class': 'card-price'}).text.strip().replace('Rp ', '').replace('.', '')
    stock = soup.find(attrs={'class': 'card-stock'}).text.strip().replace('stock: ', '')
    category = soup.find(attrs={'class': 'card-category'}).text.strip().replace('category: ', '')
    description = soup.find(attrs={'class': 'card-text'}).text.strip().replace('Description: ', '')

    dict_data = {
        'title': title,
        'price': price,
        'stock': stock,
        'category': category,
        'description': description
    }

    with open('./results/{}.json'.format(url.replace('/', '')), 'w') as outfile:
        json.dump(dict_data, outfile)


def create_csv():
    print('csv generated.....')

    files = sorted(glob.glob('./results/*.json'))

    datas = []
    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
            datas.append(data)

    df = pd.DataFrame(datas)
    df.to_csv('results.csv', index=False)


def run():
    total_pages = login()

    options = int(input("Input option number:\n"
                        "1. Collecting all urls and detail products\n"
                        "2. Creating CSV file"))

    if options == 1:
        total_urls = []
        for i in range(total_pages):
            total_urls += get_urls(i + 1)
        for url in total_urls:
            get_detail(url)
    elif options == 2:
        create_csv()
    else:
        print("Please input correct options")
        exit()

run()
