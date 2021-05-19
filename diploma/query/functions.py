import requests
from bs4 import BeautifulSoup
import json
import os
import matplotlib.pyplot as plt
from datetime import  date,timedelta
import random
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def parse(query):
    images = []
    url = "https://yandex.ru/images/search?text=" + query
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.select('.serp-item.serp-item_type_search')
    num = 1

    for item in items:
        if num < 6:
            try:
                url1 = json.loads(item.attrs['data-bem'])['serp-item']['preview'][0]['origin']['url']
                images.append(url1)
                num += 1
            except:
                continue
        else:
            break
    return images


def Popularity(url_img):
        url = 'https://yandex.ru/images/search?source=collections&rpt=imageview&url='+url_img
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        similar = soup.find_all('a', class_='other-sites__preview-link')
        return len(similar)


def graph(popularity,query,predict=False):
    plt.clf()

    dates = []
    values = []

    for k, v in popularity.items():
        date = f"{k.day}.{k.month}"
        dates.append(date)
        values.append(v)

    print(dates,values)

    plt.ylabel("Количество сайтов")
    plt.xlabel("Дата")

    if predict:
        plt.title("График прогноза на 10 дней")
        plt.plot(dates, values, color = 'yellow')
        if os.path.isfile(f'MySite\\static\img\{query}_predict.png'):
            os.remove(f'MySite\\static\img\{query}_predict.png')
        plt.savefig(f'MySite\\static\img\{query}_predict.png')
    else:
        plt.title("График популярности")
        plt.plot(dates,values)
        if os.path.isfile(f'MySite\\static\img\{query}_graph.png'):
            os.remove(f'MySite\\static\img\{query}_graph.png')

        plt.savefig(f'MySite\\static\img\{query}_graph.png')


def predict(data,query):
    values = []

    for k, v in data.items():
        values.append(v)

    n = len(data)
    Dates = [[i] for i in range(n)]

    #print(Dates,values)

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
        predict[today + timedelta(days=i+1)] = new_values[i]

    print(new_values)
    print(predict)

    graph(predict,query,True)





if __name__ == '__main__':
    #parse(query="мем")
    #Popularity("https://w7.pngwing.com/pngs/224/586/png-transparent-meme-illustration-internet-meme-rage-comic-trollface-meme-face-monochrome-head.png")

    today = date.today()
    days = []
    days.append(today - timedelta(days=24))
    days.append(today - timedelta(days=23))
    days.append(today - timedelta(days=22))
    days.append(today - timedelta(days=21))
    days.append(today - timedelta(days=20))
    days.append(today - timedelta(days=19))
    days.append(today - timedelta(days=18))
    days.append(today - timedelta(days=17))
    days.append(today - timedelta(days=16))
    days.append(today - timedelta(days=15))
    days.append(today - timedelta(days=14))
    days.append(today - timedelta(days=13))
    days.append(today - timedelta(days=12))
    days.append(today - timedelta(days=11))
    days.append(today - timedelta(days=10))
    days.append(today - timedelta(days=9))
    days.append(today - timedelta(days=8))
    days.append(today - timedelta(days=7))
    days.append(today - timedelta(days=6))
    days.append(today - timedelta(days=5))
    days.append(today - timedelta(days=4))
    days.append(today - timedelta(days=3))
    days.append(today - timedelta(days=2))
    days.append(today - timedelta(days=1))
    days.append(today)
    check = {}
    for day in days:
        check[day] = random.randint(40,80)

    #graph(check,"мем Путин")
    predict(check,"мем")