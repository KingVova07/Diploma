from django.shortcuts import render
from django.http import HttpResponse
from .main import New_MEMES,lifememes,getStatsMeme,predict,graph,NewMeme
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
    print(meme)
    data = getStatsMeme(meme)
    print(data)
    days = list(data.keys())
    Data = {}
    for day in days:
        try:
            tmp = day.replace("-","")
            today = datetime.strptime(tmp, "%Y%m%d").date()
            yesterday = today-timedelta(days=1)
            Data[day] = (data[str(today)]-data[str(yesterday)])
        except:
            continue
    try:
        graph(Data,meme)
        predict(Data,meme)
        url_img = f'img/{meme}_graph.png'
        url1_img = f'img/{meme}_predict.png'
    except Exception as e:
        print(e)
        url_img = f'img/no.png'
        url1_img = f'img/no.png'




    return render(request, "memes/life_meme.html",
                  {
                      "meme" : meme1,
                      "meme_img" : meme_img,
                      "url_img": url_img,
                      "url1_img": url1_img
                  })
