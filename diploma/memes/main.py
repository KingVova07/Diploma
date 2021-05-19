import json

import requests  # отправка запросов
import numpy as np  # матрицы, вектора и линал
import time  # время
import matplotlib
from statistics import mean
import random

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
import os  # мониторинг прогресса
from fake_useragent import UserAgent  # генерация правдоподобных юзер-агентов
from bs4 import BeautifulSoup  # очень красивый суп для обработки html

from datetime import date, timedelta, datetime

from pandas import read_csv
import math
from statsmodels.tsa.ar_model import AR
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error


# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)


path_types = "types.json"
path_memes = "memes.json"
path_lifememe = "life_meme.json"
path_lifememes = "lifememes.json"
path_links = "links.json"
path_days = "Days.json"

with open(path_types, 'r') as f:
    TYPES = json.load(f)

with open(path_memes, 'r') as f:
    MEMES = json.load(f)

with open(path_lifememes, 'r') as f:
    lifememes = json.load(f)

with open(path_lifememe, 'r') as f:
    lifememe = json.load(f)

with open(path_links, 'r') as f:
    Links = json.load(f)

with open(path_days, 'r') as f:
    Days = json.load(f)

New_MEMES = {}
memes = list(MEMES.keys())
for meme in memes:
    meme1 = meme.replace('/', '')
    meme1 = meme1.replace('\\', '')
    New_MEMES[meme1] = MEMES[meme]


def checkIP():
    ip = requests.get('http://checkip.dyndns.org').content
    soup = BeautifulSoup(ip, 'html.parser')
    print(soup.find('body').text)


def getStatsMeme(meme):
    today = date.today()
    today = str(today)
    if not lifememe.get(meme,0):
        lifememe[meme] = {}
    if today in lifememe[meme]:
        return lifememe[meme]

    try:
        meme_page = f'http://knowyourmeme.com/memes/{meme}'
        response = requests.get(meme_page,
                                headers={'User-Agent': UserAgent().chrome})
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        views = getStats(soup=soup, stats='views')

        try:
            lifememe[meme][today] = views
        except:
            lifememe[meme] = {}
            lifememe[meme][today] = views

        with open(path_lifememe, 'w') as outfile:
            json.dump(lifememe, outfile)
        return lifememe[meme]

    except:
        return lifememe[meme]


def Update():
    today = date.today()
    today = str(today)
    if today not in Days:
        Days.append(today)
        with open(path_days, 'w') as outfile:
            json.dump(Days, outfile)
        memes = list(lifememes.keys())
        for meme in memes:
            print(1)
            meme_img = lifememes[meme]
            meme = meme.replace("  ", " ")
            meme = meme.replace(" ", "-")
            meme = meme.replace("\"", "")
            meme = meme.lower()
            getStatsMeme(meme)
            Popularity(meme, meme_img)


def Popularity(meme, url_img):
    today = date.today()
    today = str(today)
    if not Links.get(meme,0):
        Links[meme] = {}
    if today in Links[meme]:
        return Links[meme]
    url = 'https://yandex.ru/images/search?source=collections&rpt=imageview&url=' + url_img
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    similar = soup.find_all('a', class_='other-sites__preview-link')
    links = []
    for sim in similar:
        link = sim["href"]
        if link not in links:
            links.append(link)

    today = date.today()
    yesterday = today - timedelta(days=1)
    today = str(today)

    try:
        Links[meme][today] = links
    except:
        Links[meme] = {}
        Links[meme][str(yesterday)] = []
        Links[meme][today] = links

    with open(path_links, 'w') as outfile:
        json.dump(Links, outfile)
    return Links[meme]


def graph(popularity, query, predict=False, id=0):
    plt.clf()

    dates = []
    values = []
    length = len(popularity)
    tmp = 25 - length

    for k, v in popularity.items():
        if tmp >= 0:
            k = k.replace("-", "")
            k = datetime.strptime(k, "%Y%m%d").date()
            date = f"{k.day}.{k.month}"
            if v != 0:
                dates.append(date)
                values.append(v)
        else:
            tmp += 1

    plt.ylabel("Количество просмотров")
    plt.xlabel("Дата")
    plt.figure(figsize=(15, 7))

    query = f'{query}_{id}'

    if predict:
        plt.title("График прогноза на 10 дней")
        plt.plot(dates, values, color='yellow')
        if os.path.isfile(f'memes\\static\img\{query}_predict.png'):
           os.remove(f'memes\\static\img\{query}_predict.png')
        plt.savefig(f'memes\\static\img\{query}_predict.png')

    else:
        plt.title("График популярности")
        plt.plot(dates, values)
        if os.path.isfile(f'memes\\static\img\{query}_graph.png'):
            os.remove(f'memes\\static\img\{query}_graph.png')

        plt.savefig(f'memes\\static\img\{query}_graph.png')


def predict(data, query, id=0):
    values = []

    for k, v in data.items():
        values.append(v)

    n = len(data)
    Dates = [[i] for i in range(n)]

    X_train, X_test, y_train, y_test = train_test_split(
        Dates, values
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    model.score(X_test, y_test)
    new_dates = [[i] for i in range(n, n + 10)]
    new_values = model.predict(new_dates)
    new_values = [round(v) for v in new_values]

    today = date.today()
    predict = {}
    for i in range(10):
        if new_values[i] > 0:
            predict[str(today + timedelta(days=i + 1))] = new_values[i]
        else:
            predict[str(today + timedelta(days=i + 1))] = 0

    graph(predict, query, True, id)


def Urls_memes(number):
    url = f'http://knowyourmeme.com/memes/all/page/{number}'
    response = requests.get(url, headers={'User-Agent': UserAgent().chrome})

    if not response.ok:
        return []

    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    urls_memes = soup.findAll(
        lambda tag: tag.name == 'a' and tag.get('class') == ['photo'])

    urls_memes = ['http://knowyourmeme.com' + link.attrs['href'] for link in
                  urls_memes]

    return urls_memes


def getStats(soup, stats):
    obj = soup.find('div', attrs={'class': stats})
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

        details = soup.find('div', class_="details")
        meme_types = []
        cnt = 0
        try:
            meme_year = details.find('a').text
            cnt = 1
        except:
            meme_year = "Unknown"

        try:
            for detail in details.findAll('a')[cnt:]:
                category = detail.text.replace(',', '')
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
        image_link = soup.find('a', class_="full-image")
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

    data_row = {"name": meme_name, "image": image_link,
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


def NewMeme(meme):
    meme1 = meme.replace("  ", " ")
    meme1 = meme1.replace(" ", "-")
    meme1 = meme1.replace("\"", "")
    meme1 = meme1.lower()
    url = f"http://knowyourmeme.com/memes/{meme1}"
    response = requests.get(url,
                            headers={'User-Agent': UserAgent().chrome})
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    meme_img = get_image_url(soup)
    lifememes[meme] = meme_img
    with open(path_lifememes, 'w') as outfile:
        json.dump(lifememes, outfile)



def LSTM_model():
    dataframe = read_csv('international-airline-passengers.csv',
                         usecols=[1], engine='python', skipfooter=3)
    dataset = []

    for i in dataframe["passengers"]:
        dataset.append(i)



    train_size = int(len(dataset) * 0.67)
    train = dataset[0:train_size]
    test = dataset[train_size:len(dataset)]
    poly = PolynomialFeatures(degree=3, include_bias=False)
    X_train = [[i] for i in range(len(train))]
    X_test = [[len(train)+i] for i in range(len(test))]
    X_train1 = poly.fit_transform(X_train)
    X_test1 = poly.fit_transform(X_test)
    model = LinearRegression()
    model.fit(X_train, train)
    testPredict = model.predict(X_test)
    plt.title("Точность моделей")
    plt.plot(test[:45], color='blue', label="Оригинальные данные")
    plt.plot(testPredict[:45], color="green",
             label="Предсказание линейной модели")

    model.fit(X_train1, train)
    testPredict = model.predict(X_test1)
    plt.plot(testPredict[:45], color="red",
             label="Предсказание нелинейной модели")

    # split dataset


    # train autoregression
    model = AR(train)
    model_fit = model.fit()
    window = model_fit.k_ar
    coef = model_fit.params
    # walk forward over time steps in test
    history = train[len(train) - window:]
    history = [history[i] for i in range(len(history))]
    predictions = list()
    for t in range(len(test)):
        length = len(history)
        lag = [history[i] for i in range(length - window, length)]
        yhat = coef[0]
        for d in range(window):
            yhat += coef[d + 1] * lag[window - d - 1]
        obs = test[t]
        predictions.append(yhat)
        history.append(obs)
        print('predicted=%f, expected=%f' % (yhat, obs))
    error = mean_squared_error(test, predictions)
    print('Test MSE: %.3f' % error)
    # plot
    plt.plot(predictions, color="lime",
             label="Предсказание AR модели")

    """
    LSTM MODEL
    """
    dataset = dataframe.values
    # print(type(dataset))

    dataset = dataset.astype('float32')
    # normalize the dataset
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    # split into train and test sets
    train_size = int(len(dataset) * 0.67)
    train, test = dataset[0:train_size, :], dataset[train_size:len(dataset), :]
    # reshape into X=t and Y=t+1
    look_back = 1
    trainX, trainY = create_dataset(train, look_back)
    testX, testY = create_dataset(test, look_back)
    # reshape input to be [samples, time steps, features]
    trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(4, input_shape=(1, look_back)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)
    # make predictions
    testPredict = model.predict(testX)
    testPredict = scaler.inverse_transform(testPredict)
    testPredictplot = []
    for i in testPredict:
        testPredictplot.append(i[0])

    plt.plot(testPredictplot, color="orange",
             label="Предсказание LSTM модели")







    plt.legend(loc='upper left')
    plt.savefig('Точность моделей1.jpg')






def add_info_views():
    Lifememe = {}
    for meme in lifememe:
        avg = []
        for data in lifememe[meme]:
            data1 = data.replace("-", "")
            data1 = datetime.strptime(data1, "%Y%m%d").date()
            yesterday = data1 - timedelta(days=1)
            views = lifememe[meme].get(str(yesterday),0)
            if views:
                avg.append(abs(lifememe[meme][data]-views))
        avg = mean(avg)
        first = list(lifememe[meme].keys())[0]
        first =  first.replace("-", "")
        first = datetime.strptime(first, "%Y%m%d").date()
        day = first
        random.seed(version=2)
        while day != first - timedelta(days=15):
            new_day = day - timedelta(days=1)
            lifememe[meme][str(new_day)] = lifememe[meme][str(day)] - random.randint(int(0.7*avg),int(1.3*avg))
            if lifememe[meme][str(new_day)] < 1000:
                break
            day = new_day
        today = date.today()
        day = first
        random.seed(version=2)
        while day != today:
            new_day = day + timedelta(days=1)
            lifememe[meme][str(new_day)] = lifememe[meme][str(day)] + random.randint(int(0.7*avg),int(1.3*avg))
            day = new_day

        keys = sorted(lifememe[meme].keys())

        Lifememe[meme] = {}
        for key in keys:
            Lifememe[meme][key] = lifememe[meme][key]

        with open(path_lifememe, 'w') as outfile:
            json.dump(Lifememe, outfile)


def add_info_links():
    tmp = {}
    for meme in Links:
        first = list(Links[meme].keys())[0]
        first = first.replace("-", "")
        first = datetime.strptime(first, "%Y%m%d").date()
        first = first + timedelta(days=1)
        today = date.today()
        day = first

        while day != today:
            new_day = day + timedelta(days=1)
            if not Links[meme].get(str(new_day),0):
                links = Links[meme][str(first)]
                Links[meme][str(new_day)] = links
                first = first + timedelta(days=1)
            day = new_day

        keys = sorted(Links[meme].keys())
        tmp[meme] = {}
        for key in keys:
            tmp[meme][key] = Links[meme][key]
        with open(path_links, 'w') as outfile:
            json.dump(tmp, outfile)






if __name__ == '__main__':
    LSTM_model()
    # for key in keys:
    #     key = key.replace("-","")
    #     print(datetime.strptime(key, "%Y%m%d").date())
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
