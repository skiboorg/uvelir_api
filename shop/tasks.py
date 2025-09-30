from .models import *
from celery import shared_task
from decimal import Decimal, InvalidOperation
import math
import json
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.conf import settings

def safe_decimal(value, default=Decimal('0.00')):
    try:
        if value in (None, '', 'null'):
            return default
        return Decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        return default

def process_image_to_webp(file_path, output_size=(1000, 1000)):
    absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
    with Image.open(absolute_path) as img:
        img = img.convert("RGBA")
        new_img = Image.new("RGBA", output_size, (255, 255, 255, 0))
        img.thumbnail(output_size, Image.Resampling.LANCZOS)
        img = ImageOps.fit(img, output_size, Image.Resampling.LANCZOS)
        x_offset = (output_size[0] - img.width) // 2
        y_offset = (output_size[1] - img.height) // 2
        new_img.paste(img, (x_offset, y_offset), img)
        buffer = BytesIO()
        new_img.save(buffer, format="WEBP")
        buffer.seek(0)
        file_name = os.path.splitext(os.path.basename(file_path))[0] + ".webp"
        return ContentFile(buffer.read(), name=file_name)

@shared_task
def updateItems(file=None):
    if file:
        data = file
    else:
        with open('export.json', 'r', encoding='utf-8') as f:
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

    # --- Категории ---
    for category in categories_elements:
        category_uuid = category.get('CategoryID')
        category_name = category.get('Name')
        subcategories = category.get('Elements', [])
        new_category, created = Category.objects.get_or_create(uid=category_uuid, name=category_name)
        if 'не выгружать' in category_name.lower() or created:
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

    # --- Материалы ---
    for material in materials:
        Material.objects.get_or_create(
            uid=material.get('ID'),
            label=material.get('Name'),
            metal=material.get('Metal'),
            probe=material.get('Probe')
        )

    # --- Покрытия ---
    for coating in coatings:
        Coating.objects.get_or_create(
            uid=coating.get('ID'),
            label=coating.get('Name')
        )

    # --- Драгоценные камни ---
    for gemstone in gemstones:
        obj, created = Fineness.objects.get_or_create(
            uid=gemstone.get('GemstoneID'),
            label=gemstone.get('Name')
        )
        if not created:
            obj.save()

    # --- Продукты ---

    incoming_uids = [item['ID'] for item in products]
    print(incoming_uids)
    Product.objects.exclude(uid__in=incoming_uids).update(is_active=False,is_in_stock=False)
    Size.objects.update(
        price=0,
        price_init=0,
        price_opt=0,
        price_opt_init=0,
        quantity=0,
        min_weight=0,
        max_weight=0,
        avg_weight=0
    )
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
            garniture_set = product.get('garniture_set', [])

            subcategory_obj = None
            if not subcategory.exists() and subcategory_filter.exists():
                subcategory_qs = SubCategory.objects.filter(filters__in=subcategory_filter)
                if subcategory_qs.exists():
                    subcategory_obj = subcategory_qs.first()
            if subcategory.exists():
                subcategory_obj = subcategory.first()

            # --- ищем или создаём продукт ---
            new_product, _ = Product.objects.get_or_create(uid=product.get('ID'))

            # обновляем данные продукта
            new_product.article = product.get('Article')
            new_product.subcategory = subcategory_obj
            new_product.coating = coating.first() if coating.exists() else None
            new_product.fineness = fineness.first() if fineness.exists() else None
            new_product.material = material.first() if material.exists() else None
            new_product.sale = False
            new_product.filter = subcategory_filter.first() if subcategory_filter.exists() else None
            new_product.is_active = False if not subcategory_obj else True
            new_product.name = product.get('Name')

            not_image = True

            # --- основное фото ---
            if filename != 'NULL':
                image_path = f'shop/product/images/{filename}'
                file_name = os.path.splitext(os.path.basename(filename))[0] + ".webp"
                if not new_product.images.filter(file__icontains=file_name, is_main=True).exists():
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

            # --- дополнительные фото ---
            for photo in anotherphoto:
                file_name = os.path.splitext(os.path.basename(photo))[0] + ".webp"
                if not new_product.images.filter(file__icontains=file_name, is_main=False).exists():
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

            #new_product.not_image = not_image

            if len(new_product.images.all()) >0 :
                new_product.not_image = False
            else:
                new_product.not_image = True

            if len(garniture_set) > 0:
                new_product.has_garniture = True
            new_product.garniture_set_uuids = ','.join(garniture_set)
            new_product.save()

            # --- размеры ---
            current_sizes_in_file = set()

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

                min_weight = safe_decimal(size.get('WeightMin'))
                max_weight = safe_decimal(size.get('WeightMax'))

                size_obj, size_created = Size.objects.get_or_create(
                    product=new_product,
                    quantity=0,
                    size=size.get('Size')
                )

                current_sizes_in_file.add(size.get('Size'))

                if not size_created:
                    if new_product.uid == '67e5a7fa-71cd-11e7-8012-2cd05a7e0d9d':
                        print('size exixt',size_obj.size)
                        print('size_obj.quantity',size_obj.quantity)
                    # суммируем количество
                    size_obj.quantity += int(size.get('Quantity', 0))

                    # обновляем цену, если новая больше
                    if price > size_obj.price:
                        size_obj.price = price
                        size_obj.price_init = price

                    if price_opt > size_obj.price_opt:
                        size_obj.price_opt = price_opt
                        size_obj.price_opt_init = price_opt

                    # обновляем min_weight только если новое меньше
                    new_min_weight = safe_decimal(size.get('WeightMin'))
                    size_obj.min_weight = new_min_weight
                    # if new_min_weight < size_obj.min_weight:
                    #     size_obj.min_weight = new_min_weight

                    # обновляем max_weight только если новое больше
                    new_max_weight = safe_decimal(size.get('WeightMax'))
                    if new_max_weight > size_obj.max_weight:
                        size_obj.max_weight = new_max_weight

                    # пересчитываем avg_weight
                    size_obj.avg_weight = (size_obj.min_weight + size_obj.max_weight) / 2
                else:
                    avg_weight = (min_weight + max_weight) / 2
                    print(product)
                    print(size_obj)
                    print('size_obj.quantity',size_obj.quantity)

                    size_obj.quantity += int(size.get('Quantity', 0))
                    size_obj.price = price
                    size_obj.price_init = price
                    size_obj.price_opt = price_opt
                    size_obj.price_opt_init = price_opt
                    size_obj.min_weight = round(min_weight, 2)
                    size_obj.max_weight = round(max_weight, 2)
                    size_obj.avg_weight = round(avg_weight, 2)


                if size_obj.price_opt == 0:
                    size_obj.product.null_opt_price = True
                    size_obj.product.save()

                price_opt_calc = math.ceil(size_obj.price_opt_init * size_obj.max_weight)
                price_calc = math.trunc((price_opt_calc * Decimal(2)) / 10) * 10
                size_obj.price_opt = price_opt_calc
                size_obj.price = price_calc

                size_obj.save()

            # --- деактивируем старые размеры, которых нет в файле ---
            # for old_size in new_product.sizes.exclude(size__in=current_sizes_in_file):
            #     old_size.delete()

            # --- пересчёт остатков ---
            quantity = sum(s.quantity for s in new_product.sizes.all())
            if quantity == 0:
                new_product.is_active = False
                new_product.is_in_stock = False
                new_product.save()

        except Exception as e:
            print('products', e)

    # --- финальная проверка категорий ---
    print('check categories')
    for product in Product.objects.all():
        try:
            if not product.subcategory.category.is_active:
                product.hidden_category = True
                product.save()
        except Exception as e:
            print('check categories', e)

    return
