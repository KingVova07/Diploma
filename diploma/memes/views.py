from django.shortcuts import render
from django.http import HttpResponse
from .main import New_MEMES,TYPES



# Create your views here.

def index(request,page = 1):
    print (page)
    memes = list(New_MEMES.keys())
    memes = memes[10*(page-1):10*page]
    Memes = []
    pages = []
    for i in range(page-2,page+3):
        if i <= 1 or i > 104:
            continue
        pages.append(i)

    print(pages)
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