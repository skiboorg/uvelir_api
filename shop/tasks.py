
from .models import *
from celery import shared_task
from decimal import Decimal

import json
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.conf import settings

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

@shared_task
def updateItems(file = None):

    Product.objects.all().delete()
    if file:
        # Если файл передан, используем его
        data = json.loads(file)
    else:
        # Если файл не передан, читаем из тестового файла
        with open('test.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

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
                try:
                    image = process_image_to_webp(image_path)
                    not_image = False
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
                    price = Decimal(price_key.replace(',', '.'))

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
                else:
                    new_size = Size.objects.create(
                        product=new_product,
                        size=size.get('Size'),
                        quantity=int(size.get('Quantity', 0)),
                        price=price,
                        min_weight=Decimal(size.get('WeightMin')),
                        max_weight=Decimal(size.get('WeightMax')),
                        avg_weight=(Decimal(size.get('WeightMin')) + Decimal(size.get('WeightMax'))) / 2
                    )
                    if new_size.price == 0:
                        new_product.is_active = False
                        new_product.save()
            x += 1
        except Exception as e:
            print(e)
            print(product)

    return
