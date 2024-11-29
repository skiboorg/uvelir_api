from decimal import Decimal

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .serializers import *
from rest_framework import generics
from .models import *
import json

from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.conf import settings

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
    page_size = 21  # Количество элементов на странице
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

                queryset = Product.objects.filter(subcategory__in=subcategories, is_active=True)
            else:
                return Product.objects.none()
        else:
            queryset = Product.objects.filter(subcategory__slug=subcategory_slug, is_active=True)

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


def process_image_to_webp(file_path, output_size=(500, 500)):
    """
    Уменьшает изображение до указанного размера, добавляет прозрачный фон и сохраняет в формате webp.
    :param file_path: Относительный путь к файлу внутри MEDIA_ROOT (например, "shop/product/images/123.jpg").
    :param output_size: Размер выходного изображения (по умолчанию 500x500).
    :return: ContentFile объекта обработанного изображения.
    """
    # Абсолютный путь к файлу
    absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
    print(absolute_path)
    # Открываем исходное изображение
    with Image.open(absolute_path) as img:
        # Преобразуем изображение в RGBA для работы с прозрачностью
        img = img.convert("RGBA")

        # Создаем пустое изображение с прозрачным фоном
        new_img = Image.new("RGBA", output_size, (255, 255, 255, 0))

        # Масштабируем изображение с сохранением пропорций
        img.thumbnail(output_size, Image.Resampling.LANCZOS)

        # Вычисляем координаты для вставки изображения по центру
        x_offset = (output_size[0] - img.width) // 2
        y_offset = (output_size[1] - img.height) // 2

        # Вставляем изображение в центр пустого фона
        new_img.paste(img, (x_offset, y_offset), img)

        # Сохраняем изображение в формате WebP
        buffer = BytesIO()
        new_img.save(buffer, format="WEBP")
        buffer.seek(0)

        # Возвращаем объект ContentFile с новым файлом
        file_name = os.path.splitext(os.path.basename(file_path))[0] + ".webp"
        return ContentFile(buffer.read(), name=file_name)

class Test1(APIView):
    def get(self, request):
        # Category.objects.all().delete()
        # SizeFilter.objects.all().delete()
        # Material.objects.all().delete()
        # Coating.objects.all().delete()
        # Fineness.objects.all().delete()
        # SubCategory.objects.all().delete()
        Product.objects.all().delete()

        with open('test.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        categories = data.get('Categories', {})
        materials_obj = data.get('Materials', {})
        coatings_obj = data.get('Coatings', {})
        gemstones_obj = data.get('Gemstones', {})
        products_obj = data.get('Products', {})
        materials = materials_obj.get('Elements', [])
        coatings = coatings_obj.get('Elements', [])
        gemstones = gemstones_obj.get('Elements', [])
        products = products_obj.get('Elements', [])
        categories_elements = categories.get('Elements', [])

        for category in categories_elements:
            category_uuid = category.get('CategoryID')
            category_name = category.get('Name')
            subcategories = category.get('Elements', [])
            new_category, _ = Category.objects.get_or_create(uid=category_uuid, name=category_name)
            for subcategory in subcategories:
                print(subcategory)
                subcategory_uuid = subcategory.get('SubcategoryID')
                subcategory_name = subcategory.get('Name')
                new_subcategory, _ = SubCategory.objects.get_or_create(
                    category=new_category,
                    uid=subcategory_uuid,
                    name=subcategory_name
                )
                filters = subcategory.get('Elements', [])
                for filter in filters:
                    filter_uuid = filter.get('FilterID')
                    filter_name = filter.get('Name')
                    new_filter, _ = SubCategoryFilter.objects.get_or_create(uid=filter_uuid, name=filter_name)
                    new_subcategory.filters.add(new_filter)
                    # sub_filters = filter.get('Elements', [])
                    # for sub_filter in sub_filters:
        for material in materials:
            Material.objects.get_or_create(
                uid=material.get('ID'),
                label=material.get('Name'),
                metal=material.get('Metal'),
                probe=material.get('Probe')
            )
        for coating in coatings:
            Coating.objects.get_or_create(
                uid=coating.get('ID'),
                label=coating.get('Name')
            )

        for gemstone in gemstones:
            Fineness.objects.get_or_create(
                uid=gemstone.get('GemstoneID'),
                label=gemstone.get('Name')
            )



        x = 0

        for product in products:
            try:
                sizes = product.get('AvailableOptions', [])
                subcategory = SubCategory.objects.filter(uid=product.get('FilterID'))
                subcategory_filter = SubCategoryFilter.objects.filter(uid=product.get('FilterID'))
                coating = Coating.objects.filter(uid=product.get('Сoating'))
                material = Material.objects.filter(uid=product.get('Materials'))
                fineness = Fineness.objects.filter(uid=product.get('Gemstones'))
                filename = product.get('FileName')
                subcategory_obj = None
                image = None
                not_image = True
                if not subcategory.exists() and subcategory_filter.exists():
                    subcategory_qs = SubCategory.objects.filter(filters__in=subcategory_filter)
                    if subcategory_qs.exists():
                        subcategory_obj = subcategory_qs.first()

                if subcategory.exists():
                    subcategory_obj = subcategory.first()

                if filename != 'NULL':
                    image_path = f'shop/product/images/{filename}'
                    not_image = False
                    try:
                        image = process_image_to_webp(image_path)
                    except:
                        image = None




                new_product, _ = Product.objects.get_or_create(
                    uid=product.get('ID'),
                    article=product.get('Article'),
                    subcategory=subcategory_obj,
                    coating=coating.first() if coating.exists() else None,
                    fineness=fineness.first() if fineness.exists() else None,
                    material=material.first() if material.exists() else None,
                    filter=subcategory_filter.first() if subcategory_filter.exists() else None,
                    is_active=False if not subcategory_obj else True,
                    name=product.get('Name'),
                    image=image,
                    not_image=not_image
                )
                # if len(sizes) == 0:
                #     new_product.is_active = False
                #     new_product.save()

                for size in sizes:
                    if subcategory_obj:
                        cat = subcategory_obj.category
                        SizeFilter.objects.get_or_create(
                            product=cat,
                            size=size.get('Size')
                        )
                    price_key = size.get('RetailPrice')
                    if price_key == '':
                        price = 0

                    else:
                        price = Decimal(price_key.replace(',','.'))

                    size_qs = Size.objects.filter(product=new_product,size=size.get('Size'))

                    if size_qs.exists():
                        size_obj = size_qs.first()
                        size_obj.quantity = size_obj.quantity + int(size.get('Quantity',0))

                        if price > size_obj.price:
                            size_obj.price = price

                        if Decimal(size.get('WeightMin')) < size_obj.min_weight:
                            size_obj.min_weight = Decimal(size.get('WeightMin'))

                        if Decimal(size.get('WeightMax')) < size_obj.max_weight:
                            size_obj.max_weight = Decimal(size.get('WeightMax'))

                        size_obj.avg_weight = (size_obj.min_weight + size_obj.max_weight) / 2
                        size_obj.save()
                    else:
                        new_size =Size.objects.create(
                            product=new_product,
                            size=size.get('Size'),
                            quantity=int(size.get('Quantity',0)),
                            price=price,
                            min_weight=Decimal(size.get('WeightMin')),
                            max_weight=Decimal(size.get('WeightMax')),
                            avg_weight=(Decimal(size.get('WeightMin')) + Decimal(size.get('WeightMax'))) / 2
                         )
                        if new_size.price == 0:
                            new_product.is_active = False
                            new_product.save()
                x+=1
            except Exception as e:
                print(e)
                print(product)



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