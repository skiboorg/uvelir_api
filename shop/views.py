import json

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .serializers import *
from rest_framework import generics
from .models import *




from .tasks import updateItems
class GetCategories(generics.ListAPIView):
    serializer_class = CategoryShortSerializer
    queryset = Category.objects.filter(is_active=True)


class GetCoatings(generics.ListAPIView):
    serializer_class = CoatingSerializer
    queryset = Coating.objects.all()

class GetFinenesses(generics.ListAPIView):
    serializer_class = FinenessSerializer
    queryset = Fineness.objects.all()

class GetMaterials(generics.ListAPIView):
    serializer_class = MaterialSerializer
    queryset = Material.objects.all()


class GetCategory(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter()
    lookup_field = 'slug'


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 24  # Количество элементов на странице
    page_size_query_param = 'page_size'
    max_page_size = 100


class GetSubCategory(generics.ListAPIView):
    serializer_class = ProductShortSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        subcategory_slug = self.kwargs.get('subcategory_slug')
        category_slug = self.request.query_params.get('category')

        # Получаем параметры фильтрации из запроса
        size_values = self.request.query_params.getlist('size')
        coating_value = self.request.query_params.get('coating')
        fineness_value = self.request.query_params.get('fineness')
        filter_value = self.request.query_params.get('filter')
        price_from = self.request.query_params.get('price__gte',0)
        price_to = self.request.query_params.get('price__lte',0)
        print(size_values)

        filters = None
        # Базовый queryset
        if subcategory_slug == 'all' and category_slug:
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                subcategories = SubCategory.objects.filter(category=category)

                if self.request.user.is_authenticated and self.request.user.is_opt_user:
                    queryset = Product.objects.filter(subcategory__in=subcategories, is_active=True)
                else:
                    queryset = Product.objects.filter(subcategory__in=subcategories, is_active=True, not_image=False)
            else:
                return Product.objects.none()
        else:
            if self.request.user.is_authenticated and self.request.user.is_opt_user:
                queryset = Product.objects.filter(subcategory__category__slug=subcategory_slug, subcategory__slug=subcategory_slug, is_active=True)
            else:
                queryset = Product.objects.filter(subcategory__category__slug=subcategory_slug,subcategory__slug=subcategory_slug, is_active=True,
                                                  not_image=False)

        # Применение фильтров
        if size_values:
            # Разбиваем строку значений на список
            #size_values_list = size_values.split(',')
            queryset = queryset.filter(sizes__size__in=size_values)

        if coating_value:
            queryset = queryset.filter(coating__value=coating_value)

        if fineness_value:
            queryset = queryset.filter(fineness__value=fineness_value)



        if price_from and price_to:
            queryset = queryset.filter(
                Q(sizes__price__gte=price_from) & Q(sizes__price__lte=price_to)
            )

        if filter_value:
            queryset = queryset.filter(filter__slug=filter_value)

        return queryset.distinct()

    def get(self, request, *args, **kwargs):
        # Получаем стандартный пагинированный ответ
        response = super().get(request, *args, **kwargs)

        subcategory_slug = self.kwargs.get('subcategory_slug')

        if subcategory_slug != 'all':
            subcategory = SubCategory.objects.get(slug=subcategory_slug)
            print('subcategory', subcategory)
            filters = subcategory.filters.all()

            filters_serializer = SubCategoryFilterSerializer(filters, many=True)
            response.data['filters'] = filters_serializer.data
        else:
            response.data['filters'] = []
        return Response(response.data)

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
    #queryset = Product.objects.filter(is_popular=True, is_active=True)

    def get_queryset(self):
        products = []
        all_uuids = Popular.objects.all()
        for uuid in all_uuids:
            products.append(Product.objects.get(uid=uuid))
        return products


class GetNewProducts(generics.ListAPIView):
    serializer_class = ProductShortSerializer
    queryset = Product.objects.filter(is_new=True, is_active=True)



class UpdateItems(APIView):
    def get(self, request):
        updateItems.delay()
        return Response({"status": "file processed"}, status=202)

    def post(self, request):
        # Проверяем, есть ли файл в запросе
        json_file = request.FILES.get("file")
        if not json_file:
            return Response({"error": "No file provided"}, status=400)

        try:
            # Читаем содержимое файла
            file_content = json_file.read().decode("utf-8")
            json_data = json.loads(file_content)  # Проверяем, что это валидный JSON

            # Передаем данные в Celery задачу
            updateItems.delay(json_data)
            return Response({"status": "file processed"}, status=202)

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON file"}, status=400)


class FavoriteView(APIView):
    def get(self, request):
        fav= Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(fav, many=True)
        return Response(serializer.data, status=200)
    
    def post(self, request):
        data = request.data
        print(data)
        product = Product.objects.get(id=data['product_id'])
        print(product)
        fav_item, created = Favorite.objects.get_or_create(product=product,user=request.user)
        if not created:
            fav_item.delete()
            message = 'Удалено из избранного'
        else:
            message = 'Добавлено в избранное'

        return Response({'message':message}, status=200)


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