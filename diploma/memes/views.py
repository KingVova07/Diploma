from django.shortcuts import render
from django.http import HttpResponse
from .main import New_MEMES,lifememes,NewMeme,Links
from .main import predict,graph,Popularity,getStatsMeme,Update

from datetime import date,timedelta,datetime




# Create your views here.

def index(request,page = 1):
    memes = list(New_MEMES.keys())
    memes = memes[10*(page-1):10*page]
    Memes = []
    pages = []
    for i in range(page-2,page+3):
        if i <= 1 or i > 104:
            continue
        pages.append(i)

    for meme in memes:
        Memes.append((meme,New_MEMES[meme]["image"]))

    return render(request, "memes/index.html",
                  {
                      "memes": Memes,
                      "pages" : pages
                  })

def memes(request,meme_id):
    meme_name = meme_id
    image =  New_MEMES[meme_id]["image"]
    views = New_MEMES[meme_id]["views"]
    origin_year =  New_MEMES[meme_id]["origin_year"]
    date_added =  New_MEMES[meme_id]["date_added"]
    videos =  New_MEMES[meme_id]["videos"]
    photos =  New_MEMES[meme_id]["photos"]
    comments =  New_MEMES[meme_id]["comments"]
    about =  New_MEMES[meme_id]["about"]
    origin =  New_MEMES[meme_id]["origin"]
    other_text =  New_MEMES[meme_id]["other_text"]
    try:
        origin_year = int(origin_year)
    except:
        origin_year = "Unknown"
    return render(request, "memes/memes.html",
                      {
                        "name": meme_name, "image" : image,
                        "origin_year": origin_year,
                        "date_added": date_added, "views": views,
                        "videos": videos, "photos": photos, "comments": comments,
                        "about": about, "origin": origin,
                        "other_text": other_text
                      })

def life(request):

    if request.method == "POST":
        meme = request.POST['meme']
        NewMeme(meme)

    Update()
    memes = list(lifememes.keys())
    Memes = []
    for meme in memes:
        Memes.append((meme,lifememes[meme]))

    return render(request, "memes/life.html",
                  {
                      "memes": Memes,
                  })



def life_meme(request,meme):
    meme1 = meme
    meme_img = lifememes[meme]
    meme = meme.replace("  ", " ")
    meme = meme.replace(" ","-")
    meme = meme.replace("\"", "")
    meme = meme.lower()

    links = Popularity(meme,meme_img)

    data = getStatsMeme(meme)
    days = list(data.keys())
    Data = {}

    Data1 = {}
    for day in days:
        try:
            tmp = day.replace("-","")
            today = datetime.strptime(tmp, "%Y%m%d").date()
            yesterday = today-timedelta(days=1)
            Data[day] = (data[str(today)]-data[str(yesterday)])

        except:
            continue
    days = list(links.keys())
    for day in days:
        Data1[day] = len(links[day])


    try:
        graph(Data,meme)
        url_img = f'img/{meme}_0_graph.png'
    except Exception as e:
        url_img = f'img/no.png'

    try:
        predict(Data, meme)
        url1_img = f'img/{meme}_0_predict.png'
    except:
        url1_img = f'img/no.png'

    try:
        graph(Data1, meme, id=1)
        url2_img = f'img/{meme}_1_graph.png'
    except Exception as e:
        url2_img = f'img/no.png'


    try:
        predict(Data1, meme, id=1)
        url3_img = f'img/{meme}_1_predict.png'
    except Exception as e:
        url3_img = f'img/no.png'

    return render(request, "memes/life_meme.html",
                  {
                      "meme" : meme1,
                      "meme_img" : meme_img,
                      "url_img": url_img,
                      "url1_img": url1_img,
                      "url2_img": url2_img,
                      "url3_img": url3_img
                  })


def Links_meme(request,meme, day = ""):
    meme1 = meme
    meme = meme.replace("  ", " ")
    meme = meme.replace(" ", "-")
    meme = meme.replace("\"", "")
    meme = meme.lower()
    links = Links[meme]
    days = list(links.keys())
    data = []


    for i in range(len(days)):
        if i == 0:
            data.append((days[i],0,0,0))

        else:
            new = list(set(links[days[i]]) - set(links[days[i-1]]))
            old = list(set(links[days[i-1]]) - set(links[days[i]]))
            data.append((days[i],len(links[days[i]]),len(new),len(old)))
            if days[i] == day:
                data = (day,links[day],new,old)
                break

    if day == "":
        return render(request,"memes/links.html",
                      {
                          "meme" : meme1,
                          "data": data
                      })


    return render(request, "memes/links_info.html",
                  {
                      "meme": meme1,
                      "data": data
                  })



