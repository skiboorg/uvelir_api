from django.urls import path,include
from . import views

urlpatterns = [
    path('all', views.GetNews.as_view()),
    path('index', views.GetIndexNews.as_view()),
    path('tags', views.GetTags.as_view()),
    path('all/<slug>', views.GetNewsItem.as_view()),

]
