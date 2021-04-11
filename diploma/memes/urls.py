from django.urls import path
from . import views

urlpatterns = [
    path("",views.index,name="index_0"),
    path("<int:page>", views.index, name="index"),
    path("<str:meme_id>",views.memes, name="memes"),
]