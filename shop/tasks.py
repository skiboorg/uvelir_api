
from .models import *
from celery import shared_task
from decimal import Decimal
import math
import json
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.conf import settings

def process_image_to_webp(file_path, output_size=(800, 800)):
    """
    Уменьшает изображение до указанного размера, добавляет прозрачный фон и сохраняет в формате webp.
    :param file_path: Относительный путь к файлу внутри MEDIA_ROOT (например, "shop/product/images/123.jpg").
    :param output_size: Размер выходного изображения (по умолчанию 500x500).
    :return: ContentFile объекта обработанного изображения.
    """
    # Абсолютный путь к файлу
    absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
    # print(absolute_path)
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

@shared_task
def updateItems(file = None):

    Product.objects.all().delete()
    if file:
        # Если файл передан, используем его
        # data = json.loads(file)
        data = file
    else:
        # Если файл не передан, читаем из тестового файла
        with open('test.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Category.objects.all().delete()
        # SizeFilter.objects.all().delete()
        # Material.objects.all().delete()
        # Coating.objects.all().delete()
        # Fineness.objects.all().delete()
        # SubCategory.objects.all().delete()

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
        new_category, created = Category.objects.get_or_create(uid=category_uuid, name=category_name)

        if created:
            new_category.is_active = False
            new_category.save()

        for subcategory in subcategories:
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
        obj, created = Fineness.objects.get_or_create(
            uid=gemstone.get('GemstoneID'),
            label=gemstone.get('Name')
        )
        if not created:
            obj.save()

    x = 0

    for product in products:
        try:
            sizes = product.get('AvailableOptions', [])
            anotherphoto = product.get('anotherphoto', [])
            subcategory = SubCategory.objects.filter(uid=product.get('FilterID'))
            subcategory_filter = SubCategoryFilter.objects.filter(uid=product.get('FilterID'))
            coating = Coating.objects.filter(uid=product.get('Сoating'))
            material = Material.objects.filter(uid=product.get('Materials'))

            fineness = Fineness.objects.filter(uid=product.get('Gemstones'))
            filename = product.get('FileName')
            garniture_set = product.get('garniture_set',[])
            subcategory_obj = None
            image = None
            not_image = True
            if not subcategory.exists() and subcategory_filter.exists():
                subcategory_qs = SubCategory.objects.filter(filters__in=subcategory_filter)
                if subcategory_qs.exists():
                    subcategory_obj = subcategory_qs.first()

            if subcategory.exists():
                subcategory_obj = subcategory.first()



            new_product, _ = Product.objects.get_or_create(
                uid=product.get('ID'),
                article=product.get('Article'),
                subcategory=subcategory_obj,
                coating=coating.first() if coating.exists() else None,
                fineness=fineness.first() if fineness.exists() else None,
                material=material.first() if material.exists() else None,
                sale=False,
                filter=subcategory_filter.first() if subcategory_filter.exists() else None,
                is_active=False if not subcategory_obj else True,
                name=product.get('Name')
            )
            # print(filename)



            if filename != 'NULL':
                image_path = f'shop/product/images/{filename}'
                try:
                    image = process_image_to_webp(image_path)
                    ProductImage.objects.create(
                        product=new_product,
                        file=image,
                        is_main=True
                    )
                    not_image = False
                except:
                    pass

            for photo in anotherphoto:
                # print(photo)
                try:
                    image_path = f'shop/product/images/{photo}'
                    image = process_image_to_webp(image_path)
                    ProductImage.objects.create(
                        product=new_product,
                        file=image,
                        is_main=False
                    )
                except:
                    pass

            new_product.not_image = not_image
            if len(garniture_set) > 0:
                new_product.has_garniture = True
            new_product.garniture_set_uuids = ','.join(garniture_set)
            new_product.save()

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
                price_opt_key = size.get('WholesalePrice')

                # print('price_key',price_key)
                # print('price_opt_key',price_opt_key)

                if price_key == '':
                    price = 0
                else:
                    price = Decimal(price_key.replace(',', '.'))

                if price_opt_key == '':
                    price_opt = 0
                else:
                    price_opt = Decimal(price_opt_key.replace(',', '.'))

                size_qs = Size.objects.filter(product=new_product, size=size.get('Size'))

                if size_qs.exists():
                    size_obj = size_qs.first()
                    size_obj.quantity = size_obj.quantity + int(size.get('Quantity', 0))

                    if price > size_obj.price:
                        size_obj.price = price

                    if Decimal(size.get('WeightMin')) < size_obj.min_weight:
                        size_obj.min_weight = Decimal(size.get('WeightMin'))

                    if Decimal(size.get('WeightMax')) < size_obj.max_weight:
                        size_obj.max_weight = Decimal(size.get('WeightMax'))

                    size_obj.avg_weight = (size_obj.min_weight + size_obj.max_weight) / 2
                    size_obj.save()

                    size = size_obj

                    if size.price_opt == 0:
                        size.product.null_opt_price = True
                        size.product.save()
                    price_opt = math.ceil(size.price_opt * size.max_weight)
                    price = math.trunc((price_opt * Decimal(2)) / 10) * 10
                    size.price_opt = price_opt
                    size.price = price
                    size.save()
                else:
                    min_weight = Decimal(size.get('WeightMin'))
                    max_weight = Decimal(size.get('WeightMax'))
                    avg_weight = (min_weight + max_weight) / 2

                    new_size = Size.objects.create(
                        product=new_product,
                        size=size.get('Size'),
                        quantity=int(size.get('Quantity', 0)),
                        price=price,
                        price_init=price,
                        price_opt=price_opt,
                        price_opt_init=price_opt,
                        min_weight=round(min_weight,2),
                        max_weight=round(max_weight,2),
                        avg_weight=round(avg_weight,2)
                    )
                    if new_size.quantity == 0:
                        new_product.is_active = False
                        new_product.save()
                   #added
                    size = new_size

                    if size.price_opt == 0:
                        size.product.null_opt_price = True
                        size.product.save()
                    price_opt = math.ceil(size.price_opt * size.max_weight)
                    price = math.trunc((price_opt * Decimal(2)) / 10) * 10
                    size.price_opt = price_opt
                    size.price = price
                    size.save()
                # added
            x += 1
        except Exception as e:
            print('products', e)
            # print(product)
    #all_sizes = Size.objects.all()
    # print('check sizes')
    # for size in all_sizes:
    #     try:
    #         if size.price_opt == 0:
    #             size.product.null_opt_price = True
    #             size.product.save()
    #         price_opt = math.ceil(size.price_opt * size.max_weight)
    #         price = math.trunc((price_opt * Decimal(2)) / 10 ) * 10
    #         size.price_opt = price_opt
    #         size.price= price
    #         size.save()
    #     except Exception as e:
    #         print('check sizes',e)
    print('check categories')
    for product in Product.objects.all():
        try:
            if not product.subcategory.category.is_active:
                product.hidden_category = True
                product.save()
        except Exception as e:
            print('check categories',e)
    return
