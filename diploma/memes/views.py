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
        if i <= 1 or i > 144:
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
    return HttpResponse("Hello world")