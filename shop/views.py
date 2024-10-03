from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .serializers import *
from rest_framework import generics
from .models import *

# class GetInstructions(APIView):
#     def get(self, request):
#         return Response("Hello World")


class GetCategories(generics.ListAPIView):
    serializer_class = CategoryShortSerializer
    queryset = Category.objects.all()

class GetCategory(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter()
    lookup_field = 'slug'


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Количество элементов на странице
    page_size_query_param = 'page_size'
    max_page_size = 100


class GetSubCategory(generics.ListAPIView):
    serializer_class = ProductShortSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        subcategory_slug = self.kwargs.get('subcategory_slug')

        # Если slug='all', возвращаем товары для всех подкатегорий в указанной категории
        if subcategory_slug == 'all':
            category_slug = self.request.query_params.get('category')

            if category_slug:
                # Получаем категорию по slug
                category = Category.objects.filter(slug=category_slug).first()

                if category:
                    # Получаем все подкатегории для данной категории
                    subcategories = SubCategory.objects.filter(category=category)

                    # Возвращаем товары, которые находятся в этих подкатегориях
                    return Product.objects.filter(subcategory__in=subcategories)
            return Product.objects.none()  # Если категория не найдена, ничего не возвращаем

        # Иначе возвращаем товары, которые находятся в подкатегории с данным slug
        return Product.objects.filter(subcategory__slug=subcategory_slug)

class GetProduct(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter()
    lookup_field = 'slug'

class GetPopularProducts(generics.ListAPIView):
    serializer_class = ProductShortSerializer
    queryset = Product.objects.filter(is_popular=True, is_active=True)


class GetNewProducts(generics.ListAPIView):
    serializer_class = ProductShortSerializer
    queryset = Product.objects.filter(is_new=True, is_active=True)

class UpdateProducts(APIView):
    def post(self, request):
        data = request.data
        for item in data:
            product_qs = Product.objects.filter(article_num=item['article_num'])
            if product_qs.exists():
                product = product_qs.first()
                product.price = item['price_ozon']
                product.price_wb = item['price_wb']
                product.wb_link = item['link_wb'].replace('\/','/')
                product.ozon_link = item['link_ozon'].replace('\/','/')
                product.save()
        return Response(status=200)


class Test(APIView):

    def get(self, request):
        import requests
        data = [
            {
                "article_num": "11",
                "Наименование": "Утюг беспроводной IR-02",
                "link_wb": "https:\/\/www.wildberries.ru\/catalog\/216809775\/detail.aspx",
                "price_wb": 1617,
                "link_ozon": "https:\/\/ozon.ru\/context\/detail\/id\/1522019621\/",
                "price_ozon": 1765
            },
        ]
        response = requests.post('https://felfri.ru/api/shop/updatetable', json=data)
        print(response.text)
        return Response(status=200)