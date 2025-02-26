from django.urls import path,include
from . import views

urlpatterns = [
    path('categories', views.GetCategories.as_view()),
    path('coatings', views.GetCoatings.as_view()),
    path('finenesses', views.GetFinenesses.as_view()),
    path('materials', views.GetMaterials.as_view()),

    path('categories/<slug>', views.GetCategory.as_view()),
    path('subcategory/<subcategory_slug>', views.GetSubCategory.as_view()),
    path('product/<slug>', views.GetProduct.as_view()),
    path('new', views.GetNewProducts.as_view()),
    path('popular', views.GetPopularProducts.as_view()),
    path('updateitems', views.UpdateItems.as_view()),

    path('search', views.ProductSearchView.as_view()),
    path('fav', views.FavoriteView.as_view()),
    path('banners', views.GetBanners.as_view()),
]
