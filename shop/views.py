import json
from unicodedata import category

from django.db.models import Q, Count
from django.db.models.expressions import result
from django.template.base import kwarg_re
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
    page_size = 48  # Количество элементов на странице
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
        filter_values = self.request.query_params.getlist('filter')
        price_from = self.request.query_params.get('price__gte', None)
        price_to = self.request.query_params.get('price__lte', None)
        is_in_stock = self.request.query_params.get('is_in_stock', '')
        ordering = self.request.query_params.get('ordering')  # Параметр сортировки

        if subcategory_slug == 'all' and category_slug:
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                subcategories = SubCategory.objects.filter(category=category)

                if self.request.user.is_authenticated and self.request.user.is_opt_user:
                    queryset = Product.objects.filter(subcategory__in=subcategories)
                else:
                    queryset = Product.objects.filter(subcategory__in=subcategories, null_opt_price=False,  is_active=True, not_image=False)
            else:
                return Product.objects.none()
        else:
            if self.request.user.is_authenticated and self.request.user.is_opt_user:
                queryset = Product.objects.filter(subcategory__slug=subcategory_slug)
            else:
                queryset = Product.objects.filter(subcategory__slug=subcategory_slug, null_opt_price=False, is_active=True, not_image=False)

        # Применение фильтров
        if size_values:
            queryset = queryset.filter(sizes__size__in=size_values)

        if coating_value:
            queryset = queryset.filter(coating__value=coating_value)

        if fineness_value:
            queryset = queryset.filter(fineness__value=fineness_value)

        print('ewre', price_from, price_to)

        if price_from and price_to:
            queryset = queryset.filter(
                sizes__price__gte=price_from,
                sizes__price__lte=price_to
            )
        elif price_from:
            queryset = queryset.filter(
                sizes__price__gte=price_from
            )
        elif price_to:
            queryset = queryset.filter(
                sizes__price__lte=price_to
            )


        if filter_values:
            queryset = queryset.filter(filter__slug__in=filter_values)

        # Применение сортировки
        if ordering:
            if ordering in ['name', '-name']:
                queryset = queryset.order_by(ordering)
            elif ordering in ['sizes__price', '-sizes__price']:
                queryset = queryset.annotate(avg_price=Avg('sizes__price'))
                queryset = queryset.order_by(ordering.replace('sizes__price', 'avg_price'))
        else:
            queryset = queryset.annotate(image_count=Count('images'))
            queryset = queryset.order_by('-image_count')  # Стандартная сортировка
        if is_in_stock == 'true':
            queryset = queryset.filter(is_in_stock=True)

        return queryset


    def get(self, request, *args, **kwargs):
        # Получаем стандартный пагинированный ответ
        response = super().get(request, *args, **kwargs)

        subcategory_slug = self.kwargs.get('subcategory_slug')
        print('subcategory_slug',subcategory_slug)
        if subcategory_slug != 'all':
            subcategory = SubCategory.objects.get(slug=subcategory_slug)
            print('subcategory', subcategory)
            filters = subcategory.filters.all()
            size_filters = subcategory.size_filters.all()

            filters_serializer = SubCategoryFilterSerializer(filters, many=True)
            sizes_serializer = SubcategorySizeFilterSerializer(size_filters, many=True)
            response.data['filters'] = filters_serializer.data
            response.data['sizes'] = sizes_serializer.data
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
            try:
                products.append(Product.objects.get(uid=uuid))
            except Product.DoesNotExist:
                pass
        return products

class GetRecomendedProducts(generics.ListAPIView):
    serializer_class = ProductShortSerializer

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        product = Product.objects.get(id=product_id)
        products = Product.objects.filter(subcategory_id=product.subcategory_id,is_active=True).order_by('?')[:5]
        return products


class GetNewProducts(generics.ListAPIView):
    serializer_class = ProductShortSerializer
    queryset = Product.objects.filter(is_new=True, is_active=True)



class TestItems(APIView):
    def get(self, request):
        from django.db.models import Count
        result = []
        # Найти все дублирующиеся продукты
        duplicate_names = Product.objects.values('name').annotate(
            count=Count('id')
        ).filter(count__gt=1, name__isnull=False).values_list('name', flat=True)

        # Найти все объекты с дублирующимися именами
        duplicate_products = Product.objects.filter(name__in=duplicate_names)

        print(f"Найдено {duplicate_products.count()} дублирующихся продуктов")

        # Выполнить save() для каждого дубликата
        for product in duplicate_products:
            product.save()  # Это вызовет обновление записи
            result.append(f"Перезаписан продукт: ID {product.id}, Name: '{product.name}'")
            print(f"Перезаписан продукт: ID {product.id}, Name: '{product.name}'")
        return Response({"status": result}, status=200)

class UpdateItems(APIView):
    def get(self, request):
        updateItems()
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

class ProductSearchView(generics.ListAPIView):
    pagination_class = StandardResultsSetPagination
    serializer_class = ProductShortSerializer

    def get_queryset(self):
        query = self.request.GET.get('q', '')  # Получаем значение параметра "q" из GET-запроса
        query_lower = query.lower()

        text_filter = (
                Q(name_lower__icontains=query_lower) |
                Q(article_lower__icontains=query) |
                Q(fineness__label_lower__icontains=query_lower)
        )

        base_filter = Q(subcategory__category__is_active=True) & text_filter

        # Фильтрация по пользователю
        if self.request.user.is_authenticated and self.request.user.is_opt_user:
            qs = Product.objects.filter(base_filter)
        else:
            qs = Product.objects.filter(base_filter, is_active=True)

        print(qs)
        for product in qs:
            print(product.subcategory.category.is_active)

        # Аннотация количества изображений и сортировка сначала с фото
        qs = qs.annotate(image_count=Count('images')).order_by('-image_count')

        return qs


class ProductSearchViewOld(generics.ListAPIView):
    pagination_class = StandardResultsSetPagination
    serializer_class = ProductShortSerializer

    def get_queryset(self):
        query = self.request.GET.get('q', '')  # Получаем значение параметра "q" из GET-запроса
        keywords = query.split()

        # Базовый запрос для поиска активных продуктов
        # products = Product.objects.filter(name_lower__icontains=query.lower(), is_active=True)

        if self.request.user.is_authenticated and self.request.user.is_opt_user:
            products = Product.objects.filter(
                Q(name_lower__icontains=query.lower()) |
                Q(article_lower__icontains=query) |
                Q(fineness__label_lower__icontains=query)
            )
            return products

        products = Product.objects.filter(
            Q(name_lower__icontains=query.lower()) |
            Q(article_lower__icontains=query) |
            Q(fineness__label_lower__icontains=query),
            is_active=True
        )
        return products



class GetBanners(generics.ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer


class SelectionRetriveView(generics.RetrieveAPIView):
    serializer_class = SelectionSerializer
    queryset = Selection.objects.all()
    lookup_field = 'promo'

class SelectionAPIView(APIView):
    def get(self, request):
        qs = Selection.objects.all()
        serializer = SelectionSerializer(qs, many=True)
        return Response(serializer.data, status=202)

    def post(self, request):
        print(request.data)
        id = request.data.get('id', None)
        print(request.data.get('is_sale') in ['true', 'True', True, 1, '1'])
        image = request.data.get('image', None)
        if id:
            selection_obj = Selection.objects.get(id=id)
            selection_obj.name=request.data.get('name')
            selection_obj.promo=request.data.get('promo')
            selection_obj.is_sale=request.data.get('is_sale') in ['true', 'True', True, 1, '1']

            selection = selection_obj
            selection_obj.items.all().delete()
            if image:
                selection_obj.image = image
            selection_obj.save()
        else:
            new_selection = Selection.objects.create(
                user=request.user,
                name=request.data.get('name'),
                promo=request.data.get('promo'),
                is_sale=request.data.get('is_sale') in ['true', 'True', True, 1, '1'],

            )
            selection = new_selection
            if image:
                new_selection.image = image
                new_selection.save()
        items_raw = request.data.get('items')
        if items_raw:
            try:
                items = json.loads(items_raw)
            except (TypeError, json.JSONDecodeError):
                items = []
        else:
            items = []

        for item in items:
            SelectionItem.objects.create(
                selection=selection,
                item_id=item.get('id'),
            )

        return Response(status=200)

    def delete(self, request):
        pk = request.data.get("pk")
        if not pk:
            return Response({"error": "pk is required"}, status=400)

        try:
            selection = Selection.objects.get(pk=pk, user=request.user)
            selection.delete()
            return Response({"status": "deleted"}, status=204)
        except Selection.DoesNotExist:
            return Response({"error": "Not found"}, status=404)