import json

import requests      # отправка запросов
import numpy as np   # матрицы, вектора и линал
import pandas as pd  # таблички и операции с ними
import time          # время
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import os
from tqdm import tqdm                 # мониторинг прогресса
from fake_useragent import UserAgent  # генерация правдоподобных юзер-агентов
from bs4 import BeautifulSoup         # очень красивый суп для обработки html

import argparse # чтение аргументов из коммандной строки

import socks   # подключение к тору
import smtplib
import socket
import sys
from datetime import  date,timedelta,datetime


path_types = "types.json"
path_memes = "memes.json"
path_lifememe = "life_meme.json"
path_lifememes = "lifememes.json"

with open(path_types, 'r') as f:
    TYPES = json.load(f)

with open(path_memes, 'r') as f:
    MEMES = json.load(f)

with open(path_lifememes, 'r') as f:
    lifememes = json.load(f)

with open(path_lifememe, 'r') as f:
    lifememe = json.load(f)


New_MEMES = {}
memes = list(MEMES.keys())
for meme in memes:
    meme1 = meme.replace('/','')
    meme1 = meme1.replace('\\','')
    New_MEMES[meme1] = MEMES[meme]


def checkIP():
    ip = requests.get('http://checkip.dyndns.org').content
    soup = BeautifulSoup(ip, 'html.parser')
    print(soup.find('body').text)


def getStatsMeme(meme):
    meme_page = f'http://knowyourmeme.com/memes/{meme}'
    response = requests.get(meme_page,
                            headers={'User-Agent': UserAgent().chrome})
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    views = getStats(soup=soup, stats='views')
    today = date.today()
    today = str(today)
    lifememe[meme][today] = views
    with open(path_lifememe, 'w') as outfile:
        json.dump(lifememe, outfile)
    return lifememe[meme]

def graph(popularity,query,predict=False):
    plt.clf()

    dates = []
    values = []

    for k, v in popularity.items():
        k = k.replace("-","")
        k = datetime.strptime(k, "%Y%m%d").date()
        date = f"{k.day}.{k.month}"
        dates.append(date)
        values.append(v)

    print(dates,values)

    plt.ylabel("Количество просмотров")
    plt.xlabel("Дата")

    if predict:
        plt.title("График прогноза на 10 дней")
        plt.plot(dates, values, color = 'yellow')
        if os.path.isfile(f'memes\\static\img\{query}_predict.png'):
            os.remove(f'memes\\static\img\{query}_predict.png')
        plt.savefig(f'memes\\static\img\{query}_predict.png')
    else:
        plt.title("График популярности")
        plt.plot(dates,values)
        if os.path.isfile(f'memes\\static\img\{query}_graph.png'):
            os.remove(f'memes\\static\img\{query}_graph.png')

        plt.savefig(f'memes\\static\img\{query}_graph.png')


def predict(data,query):
    values = []

    for k, v in data.items():
        values.append(v)

    n = len(data)
    Dates = [[i] for i in range(n)]

    print(Dates,values)

    X_train, X_test, y_train, y_test = train_test_split(
        Dates, values
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    model.score(X_test,y_test)
    new_dates = [[i] for i in range(n,n+10)]
    new_values = model.predict(new_dates)
    new_values = [round(v) for v in new_values]

    today = date.today()
    predict = {}
    for i in range(10):
        predict[str(today + timedelta(days=i+1))] = new_values[i]

    print(new_values)
    print(predict)

    graph(predict,query,True)



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
                    TYPES.append(category)

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
    print(meme_name)

    meme_about, meme_origin, other_text = getText(soup=soup)
    if meme_name == "Unknown":
        return "error"

    data_row = {"name": meme_name, "image" : image_link,
                "type": meme_type, "origin_year": meme_year,
                "date_added": date, "views": views,
                "videos": videos, "photos": photos, "comments": comments,
                "about": meme_about, "origin": meme_origin,
                "other_text": other_text}

    data_row1 = {"image": image_link,
                "type": meme_type, "origin_year": meme_year,
                "date_added": date, "views": views,
                "videos": videos, "photos": photos, "comments": comments,
                "about": meme_about, "origin": meme_origin,
                "other_text": other_text}

    MEMES[meme_name] = data_row1


    return data_row



if __name__ == '__main__':
    data = getStatsMeme("doge")
    print(data)
    keys = list(data.keys())
    for key in keys:
        key = key.replace("-","")
        print(datetime.strptime(key, "%Y%m%d").date())
    # print(len(MEMES))
    # print(len(TYPES))
    #
    #
    #
    #
    # final_df = pd.DataFrame(
    # columns=['name', 'image', 'type', 'origin_year',
    #          'date_added', 'views', 'videos', 'photos', 'comments',
    #          'about', 'origin', 'other_text'])
    #
    # checkIP()
    # socks.set_default_proxy(socks.SOCKS5, "localhost",9150)
    # socket.socket = socks.socksocket
    #
    #
    # for i in range(1,1001):
    #
    #
    #         checkIP()
    #
    #         memes = Urls_memes(i)
    #
    #         print(f'page {i}')
    #         cnt = 0
    #
    #         for meme in memes:
    #             try:
    #                 if "https" in meme:
    #                     continue
    #                 print(meme)
    #                 cnt += 1
    #                 data = getMemeData(meme)
    #                 if data == "error":
    #                     continue
    #                 final_df = final_df.append(data, ignore_index=True)
    #             except:
    #                 continue
    #
    #         with open(path_types, 'w') as outfile:
    #             json.dump(TYPES, outfile)
    #
    #         with open(path_memes, 'w') as outfile:
    #             json.dump(MEMES, outfile)
    #
    #
    # print(cnt)
    #
    #
    #
    # final_df.to_csv(f'MEMES_{1}_{1001}.csv')
    #
