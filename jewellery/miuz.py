import re

import lxml
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from numba import njit,jit

def get_max_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36'
    }
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features='lxml')
    page = int(soup.find_all('a',class_ = 'js-catalog-pagination b-pagination__link')[-1].text)
    return page


def get_posts():
    catalog = ['rings','earrings','pendants','bracelets','necklace','chain']
    df = pd.DataFrame()

    for i in catalog:
        url_pages = f'https://miuz.ru/catalog/{i}/?from=newhome-{i}-categorii'
        max_page = get_max_page(url_pages)
        for j in range(1,max_page+1):
            data = []
            print(f'Парсим категорию {i}, Страницу №{j}')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36'
            }
            url = f'https://miuz.ru/catalog/{i}/page={j}/?from=newhome-{i}-categorii'
            req = requests.get(url,headers=headers)
            soup = BeautifulSoup(req.text, features='lxml')
            items = soup.find_all('div', class_="product")
            for item in items:
                group = i
                title = item.find('a').get('title')
                search_old_price = item.find('div', class_ = 'product__price-old')
                if search_old_price == None:
                    old_price = 0
                else:
                    old_price = item.find('div', class_ = 'product__price-old').text.strip().replace(' ','')
                search_new_price = item.find('div', class_ = 'product__price-new')
                if search_new_price == None:
                    new_price = item.find('div', class_ = 'product__price').find('span', class_ =
                    'product__price-val').text.strip().replace(' ','')
                else:
                    new_price = item.find('div', class_='product__price-new').find('span', class_=
                    'product__price-val').text.strip().replace(' ', '')
                search_discount = item.find('div',class_ = 'product__price-discount')
                if search_discount == None:
                    discount = 0
                else:
                    discount = item.find('div', class_='product__price-discount').text.strip().replace('%', '')
                link = f'https://miuz.ru{item.find("a").get("href")}'
                response = requests.get(link,headers=headers)
                soup = BeautifulSoup(response.text, features='lxml')
                try:
                    metall = soup.find_all('div', class_='detail__item-option')[0].find('span',class_ = 'href').text.strip()
                    wieght_search = soup.find_all('div', class_='detail__item-option')[1]
                    wieght_search.span.decompose()
                except:
                    continue
                data.append({'Группа': group, 'title': title, 'Старая цена': old_price, 'Новая цена': new_price,
                             'Скидка': discount,'Металл': metall, 'Вес': wieght_search.text.strip(), 'Ссылка': link,
                             'Брэнд':'miuz'})
                time.sleep(0.1)

            df = df._append(data,ignore_index=True)
            print(f'Длинна фрейма {len(df)}')
    df.to_csv('miuz.csv',encoding='utf-8-sig')

get_posts()



