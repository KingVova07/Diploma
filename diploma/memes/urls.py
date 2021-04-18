from django.urls import path
from . import views

urlpatterns = [
    path("",views.index,name="index_0"),
    path("<int:page>", views.index, name="index"),
    path("mem/<str:meme_id>",views.memes, name="memes"),
    path("life", views.life,name = "life"),
    path("life/<str:meme>", views.life_meme,name = "life_meme"),
    path("links/<str:meme>", views.Links_meme, name = "links"),
    path("links/info/<str:meme>/<str:day>", views.Links_meme, name="links_info")
]