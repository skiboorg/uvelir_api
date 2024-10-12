from django.urls import path,include
from . import views

urlpatterns = [
    path('categories', views.GetCategories.as_view()),
    path('coatings', views.GetCoatings.as_view()),
    path('finenesses', views.GetFinenesses.as_view()),

    path('categories/<slug>', views.GetCategory.as_view()),
    path('subcategory/<subcategory_slug>', views.GetSubCategory.as_view()),
    path('product/<slug>', views.GetProduct.as_view()),
    path('new', views.GetNewProducts.as_view()),
    path('popular', views.GetPopularProducts.as_view()),
    path('updateitems', views.Test1.as_view()),
    path('test', views.Test.as_view()),
    path('search', views.ProductSearchView.as_view()),
]
