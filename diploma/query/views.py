from django.shortcuts import render
from django.http import HttpResponse
from .functions import parse, Popularity,graph,predict
from datetime import date,timedelta
import random

queries = []
images = {}

# Create your views here.



def index(request):
    if request.method == "POST":
        query = request.POST['query']
        q = Queriesdb(querydb=query)
        q.save()
        images[query] = {}
        tmp = parse(query)
        queries.append(query)
        for i in range(5):
            images[query][f'url{i}'] = tmp[i]

    return render(request, "MySite/index.html",
    {
        "queries" : queries
    })


def Query(request,query_id):

    print(query_id)
    curr_query = images[query_id]
    print(query_id)
    urls = []

    for i in range(5):
        urls.append(curr_query[f"url{i}"])

    popularity = {}
    popularity[query_id] = {}
    today = date.today()
    print(today)

    #временное решение
    days = []
    days.append(today - timedelta(days=9))
    days.append(today - timedelta(days=8))
    days.append(today - timedelta(days=7))
    days.append(today - timedelta(days=6))
    days.append(today - timedelta(days=5))
    days.append(today - timedelta(days=4))
    days.append(today - timedelta(days=3))
    days.append(today - timedelta(days=2))
    days.append(today - timedelta(days=1))
    for day in days:
        popularity[query_id][day] = random.randint(40,80)
    #конец временного решения

    popularity[query_id][today] = Popularity(urls[0])
    graph(popularity[query_id],query_id)
    predict(popularity[query_id],query_id)

    url_img = f'img/{query_id}_graph.png'
    url1_img = f'img/{query_id}_predict.png'


    return render(request, "MySite/Query.html",
            {
                      "urls": urls,
                      "query": query_id,
                      "url_img": url_img,
                      "url1_img": url1_img
            })
