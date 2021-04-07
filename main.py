import json

import requests      # отправка запросов
import numpy as np   # матрицы, вектора и линал
import pandas as pd  # таблички и операции с ними
import time          # время

from tqdm import tqdm                 # мониторинг прогресса
from fake_useragent import UserAgent  # генерация правдоподобных юзер-агентов
from bs4 import BeautifulSoup         # очень красивый суп для обработки html

import argparse # чтение аргументов из коммандной строки

import socks   # подключение к тору
import socket
import sys


path = "types.json"

with open(path, 'r') as f:
    TYPES = json.load(f)




def Urls_memes(number):

    url = f'http://knowyourmeme.com/memes/all/page/{number}'
    response = requests.get(url, headers={'User-Agent': UserAgent().chrome})

    if not response.ok:
        return []

    html = response.content
    soup = BeautifulSoup(html,'html.parser')

    urls_memes = soup.findAll(lambda tag: tag.name == 'a' and tag.get('class') == ['photo'])


    urls_memes = ['http://knowyourmeme.com' + link.attrs['href'] for link in urls_memes]

    return urls_memes


def getStats(soup, stats):

    obj = soup.find('div',attrs={'class': stats})
    obj = str(obj['title'])
    i = 0
    while obj[i] != " ":
        i += 1

    obj = obj[0:i]
    obj = int(obj.replace(',', ''))
    return obj


def getProperties(soup):
    try:
        meme_name = soup.find('section', attrs={'class': 'info wide'}).find(
            'h1').text.strip()


        details = soup.find('div', class_ = "details")
        meme_types = []
        cnt = 0
        try:
            meme_year = details.find('a').text
            cnt = 1
        except:
            meme_year = "Unknown"

        try:
            for detail in details.findAll('a')[cnt:]:
                category = detail.text.replace(',','')
                meme_types.append(category)
                if category is not TYPES:
                    cnt_types = len(TYPES)
                    TYPES[cnt_types] = category

        except:
            meme_types = "Unknown"



    except:
        meme_name = "Unknown"
        meme_types = "Unknown"
        meme_year = "Unknown"


    return meme_name, meme_types, meme_year


def getText(soup):

    # достаём все тексты под картинкой
    body = soup.find('section', attrs={'class': 'bodycopy'})

    meme_about = body.find('p')
    meme_about = "" if not meme_about else meme_about.text

    meme_origin = body.find(text='Origin') or body.find(text='History')
    meme_origin = "" if not meme_origin else meme_origin.parent.find_next().text

    # весь остальной текст (если он есть) можно запихнуть в одно текстовое поле
    if body.text:
        other_text = body.text.strip().split('\n')[4:]
        other_text = " ".join(other_text).strip()
    else:
        other_text = ""

    return meme_about, meme_origin, other_text


def get_image_url(soup):
    try:
        image_link = soup.find('a', class_ = "full-image")
        return image_link["href"]
    except:
        return "Unknown"

def getMemeData(meme_page):

    response = requests.get(meme_page,
                            headers={'User-Agent': UserAgent().chrome})


    if not response.ok:
        return response.status_code

    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    image_link = get_image_url(soup)
    views = getStats(soup=soup, stats='views')
    videos = getStats(soup=soup, stats='videos')
    photos = getStats(soup=soup, stats='photos')
    comments = getStats(soup=soup, stats='comments')

    date = soup.find('abbr', attrs={'class': 'timeago'}).attrs['title']

    meme_name, meme_type, meme_year = getProperties(soup=soup)

    meme_about, meme_origin, other_text = getText(soup=soup)

    data_row = {"name": meme_name, "image" : image_link,
                "type": meme_type, "origin_year": meme_year,
                "date_added": date, "views": views,
                "videos": videos, "photos": photos, "comments": comments,
                "about": meme_about, "origin": meme_origin,
                "other_text": other_text}

    return data_row



if __name__ == '__main__':
    final_df = pd.DataFrame(
    columns=['name', 'image', 'type', 'origin_year',
             'date_added', 'views', 'videos', 'photos', 'comments',
             'about', 'origin', 'other_text'])

    socks.set_default_proxy(socks.SOCKS5, "localhost",9150)
    socket.socket = socks.socksocket


    for i in range(2,102):

        for j in range(5):
            memes = Urls_memes(i)
            if memes:
                break
            else:
                time.sleep(20)

        print(f'page {i}')
        cnt = 0

        for meme in memes:
            print(meme)
            cnt += 1
            final_df = final_df.append(getMemeData(meme), ignore_index=True)


    print(cnt)
    with open(path, 'w') as outfile:
        json.dump(TYPES, outfile)
    final_df.to_csv(f'MEMES_{2}_{101}.csv')

