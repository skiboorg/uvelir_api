from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .serializers import *
from rest_framework import generics
from .models import *
import json



class GetCategories(generics.ListAPIView):
    serializer_class = CategoryShortSerializer
    queryset = Category.objects.all()


class GetCoatings(generics.ListAPIView):
    serializer_class = CoatingSerializer
    queryset = Coating.objects.all()

class GetFinenesses(generics.ListAPIView):
    serializer_class = FinenessSerializer
    queryset = Fineness.objects.all()

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
        category_slug = self.request.query_params.get('category')

        # Получаем параметры фильтрации из запроса
        size_values = self.request.query_params.get('size')
        coating_value = self.request.query_params.get('coating')
        fineness_value = self.request.query_params.get('fineness')
        price_from = self.request.query_params.get('price__gte',0)
        price_to = self.request.query_params.get('price__lte',0)
        print(price_from, price_to)

        # Базовый queryset
        if subcategory_slug == 'all' and category_slug:
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                subcategories = SubCategory.objects.filter(category=category)
                queryset = Product.objects.filter(subcategory__in=subcategories)
            else:
                return Product.objects.none()
        else:
            queryset = Product.objects.filter(subcategory__slug=subcategory_slug)

        # Применение фильтров
        if size_values:
            # Разбиваем строку значений на список
            size_values_list = size_values.split(',')
            queryset = queryset.filter(sizes__size__in=size_values_list)

        if coating_value:
            queryset = queryset.filter(coating__value=coating_value)

        if fineness_value:
            queryset = queryset.filter(fineness__value=fineness_value)

        if price_from and price_to:
            queryset = queryset.filter(
                Q(sizes__price__gte=price_from) & Q(sizes__price__lte=price_to)
            )

        return queryset.distinct()
    # def get_queryset(self):
    #     subcategory_slug = self.kwargs.get('subcategory_slug')
    #
    #     # Если slug='all', возвращаем товары для всех подкатегорий в указанной категории
    #     if subcategory_slug == 'all':
    #         category_slug = self.request.query_params.get('category')
    #
    #         if category_slug:
    #             # Получаем категорию по slug
    #             category = Category.objects.filter(slug=category_slug).first()
    #
    #             if category:
    #                 # Получаем все подкатегории для данной категории
    #                 subcategories = SubCategory.objects.filter(category=category)
    #
    #                 # Возвращаем товары, которые находятся в этих подкатегориях
    #                 return Product.objects.filter(subcategory__in=subcategories)
    #         return Product.objects.none()  # Если категория не найдена, ничего не возвращаем
    #
    #     # Иначе возвращаем товары, которые находятся в подкатегории с данным slug
    #     return Product.objects.filter(subcategory__slug=subcategory_slug)

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

class Test1(APIView):
    def get(self, request):
        with open('test.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        categories = data.get('Categories', [])
        categories_elements = categories.get('Elements', [])
        print(categories_elements[0])
        # for category in categories_elements:
        #     category_uuid = category.get('ID')
        #     category_name = category.get('Name')
        #     print(category_uuid, category_name)
        #     category_elements = categories.get('Elements', [])
        #     for category_element in category_elements:
        #         subcategories = category_element.get('Elements', [])
        #         for subcategory in subcategories:
        #             print(subcategory.get('Name'))
        # print(json.dumps(elements[1], indent=4, ensure_ascii=False))

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

class ProductSearchView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')  # Получаем значение параметра "q" из GET-запроса
        keywords = query.split()

        # Базовый запрос для поиска активных продуктов
        products = Product.objects.filter(is_active=True)

        # Фильтрация по каждому ключевому слову
        for keyword in keywords:
            products = products.filter(
                Q(name__icontains=keyword) |
                Q(coating__label__icontains=keyword) |
                Q(fineness__label__icontains=keyword) |
                Q(sizes__size__icontains=keyword)
            ).distinct()

        # Сериализуем результаты
        serializer = ProductShortSerializer(products, many=True)
        return Response(serializer.data)