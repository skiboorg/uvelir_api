from django.urls import path,include
from . import views


urlpatterns = [
    path('', views.OrderView.as_view()),
    path('delivery', views.GetDeliveries.as_view()),
    path('payment', views.GetPayments.as_view()),



]
