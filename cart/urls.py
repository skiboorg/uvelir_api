from django.urls import path,include
from . import views


urlpatterns = [
    path('', views.CartView.as_view()),
    path('del', views.CartDel.as_view()),



]
