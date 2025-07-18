from django.db import models
from pytils.translit import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django_resized import ResizedImageField
from random import choices
import string
import random


class Material(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False)
    label = models.CharField('Название', max_length=255, blank=False, null=False)
    value = models.CharField('ЧПУ', max_length=255, blank=True, null=True)
    metal = models.CharField('Метал', max_length=255, blank=True, null=True)
    probe = models.CharField('Проба', max_length=255, blank=True, null=True)
    def save(self, *args, **kwargs):

        self.value = slugify(self.label)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.label}'

    class Meta:

        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'


class Fineness(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False)
    label = models.CharField('Название', max_length=255, blank=False, null=False)
    label_lower = models.CharField('Название', max_length=255, blank=True, null=True)
    value = models.CharField('ЧПУ', max_length=255, blank=True, null=True)
    def save(self, *args, **kwargs):

        self.value = slugify(self.label)
        self.label_lower = self.label.lower()
        super().save(*args, **kwargs)
    def __str__(self):
        return f'{self.label}'
    class Meta:

        verbose_name = 'Вставка'
        verbose_name_plural = 'Вставки'


class Coating(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False)
    label = models.CharField('Название', max_length=255, blank=False, null=False)
    value = models.CharField('ЧПУ', max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.value = slugify(self.label)
        super().save(*args, **kwargs)
    def __str__(self):
        return f'{self.label}'
    class Meta:
        verbose_name = 'Покрытие'
        verbose_name_plural = 'Покрытия'

class Category(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    uid = models.CharField(max_length=255, blank=False, null=False)
    icon = ResizedImageField(size=[20, 20], quality=95, force_format='WEBP', upload_to='shop/category/icon',
                             blank=True, null=True)
    image = ResizedImageField(size=[420, 420], quality=95, force_format='WEBP', upload_to='shop/category/images',
                              blank=True, null=True)
    coatings = models.ManyToManyField(Coating, blank=True, null=True)
    materials = models.ManyToManyField(Material, blank=True, null=True)
    name = models.CharField('Название', max_length=255, blank=False, null=False)
    slug = models.CharField('ЧПУ', max_length=255,blank=True, null=True)
    short_description = models.TextField('Короткое описание', blank=True, null=False)
    html_content = CKEditor5Field('SEO текст', blank=True, null=False)
    items_count = models.IntegerField('Кол-во товаров', default=0, null=True)
    is_active = models.BooleanField('Отображать?', default=True, null=False)
    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):

        exist_cat = Category.objects.filter(slug=slugify(self.name))
        if exist_cat.exists():
            self.slug = f'{slugify(self.name)}-{"".join(random.choices(string.ascii_letters + string.digits, k=3))}'
        else:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('order_num',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class SizeFilter(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    product = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=False,
                                related_name='size_filters')
    size = models.CharField('Размер', max_length=20, blank=True, null=True)
    is_active = models.BooleanField('Отображать?', default=True, null=False)

    class Meta:
        ordering = ('order_num',)



class SubCategoryFilter(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField('Название', max_length=255, blank=False, null=False)
    slug = models.CharField('ЧПУ', max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):

        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class SubCategory(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    uid = models.CharField(max_length=255, blank=False, null=False)
    filters = models.ManyToManyField(SubCategoryFilter, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, null=True, related_name='sub_categories')
    name = models.CharField('Название', max_length=255, blank=False, null=False)
    slug = models.CharField('ЧПУ', max_length=255,blank=True, null=True)
    image = ResizedImageField(size=[420, 420], quality=95, force_format='WEBP', upload_to='shop/category/images',
                              blank=True, null=True)
    short_description = models.TextField('Короткое описание', blank=True, null=False)
    html_content = CKEditor5Field('SEO текст', blank=True, null=False)
    items_count = models.IntegerField('Кол-во товаров', default=0, null=True)
    is_active = models.BooleanField('Отображать?', default=True, null=False)
    is_default = models.BooleanField('Открывать по-умолчанию?', default=False, null=False)

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        exist_subcat = SubCategory.objects.filter(slug=slugify(self.name))
        if exist_subcat.exists():
            self.slug = f'{slugify(self.name)}-{"".join(random.choices(string.ascii_letters + string.digits, k=3))}'
        else:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('order_num',)
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

class SubcategorySizeFilter(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    product = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=False,
                                related_name='size_filters')
    size = models.CharField('Размер', max_length=20, blank=True, null=True)
    is_active = models.BooleanField('Отображать?', default=True, null=False)

    class Meta:
        ordering = ('order_num',)


class Product(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    article = models.CharField('Артикул',max_length=100,blank=True, null=True)
    article_lower = models.CharField('Артикул',max_length=100,blank=True, null=True)
    subcategory = models.ForeignKey(SubCategory,blank=True,null=True,on_delete=models.CASCADE, related_name='products')
    coating = models.ForeignKey(Coating,blank=True,null=True,on_delete=models.CASCADE, related_name='Покрытие')
    fineness = models.ForeignKey(Fineness,blank=True,null=True,on_delete=models.CASCADE, related_name='Вставка')
    material = models.ForeignKey(Material,blank=True,null=True,on_delete=models.CASCADE, related_name='Материал')
    filter = models.ForeignKey(SubCategoryFilter,blank=True,null=True,on_delete=models.CASCADE, related_name='Фильтр')
    is_new = models.BooleanField('Новинка', default=False, null=False)
    is_popular = models.BooleanField('Популярный', default=False, null=False)
    is_active = models.BooleanField('Отображать?', default=True, null=False)
    is_in_stock = models.BooleanField('В наличии?', default=True, null=False)
    sale = models.BooleanField('Распродажа',default=False, null=False)
    not_image = models.BooleanField(default=False, null=False)
    null_opt_price = models.BooleanField(default=False, null=False)
    has_garniture = models.BooleanField(default=False, null=False)
    hidden_category = models.BooleanField(default=False, null=False)

    image = models.ImageField(upload_to='shop/product/images_fixed', blank=True, null=True)

    name = models.CharField('Название', max_length=255, blank=False, null=True)
    name_lower = models.CharField('Название', max_length=255, blank=True, null=True, editable=False)
    slug = models.CharField('ЧПУ',max_length=255,
                            help_text='Если не заполнено, создается на основе поля Назавание',
                            blank=True, null=True, editable=False)
    short_description = models.TextField('Короткое описание', blank=True, null=False)
    description = CKEditor5Field('Описание', blank=True, null=True, config_name='extends')
    items_count = models.IntegerField('Кол-во товаров', default=0, null=True)
    garniture_set_uuids = models.TextField(blank=True, null=True)
    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ('-image',)
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def get_product_url(self):
        category = getattr(self.subcategory, 'category', None)
        if self.subcategory and category:
            return f"https://sh44.ru/catalog/{category.slug}/{self.subcategory.slug}/{self.slug}"
        return ""

    def have_image(self):
        return self.images.count() > 0

    def save(self, *args, **kwargs):
        base_slug = slugify(self.name) if self.name else ''
        if not self.slug:
            self.slug = base_slug

        # Проверяем наличие других товаров с таким же slug
        qs = Product.objects.filter(slug=self.slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)  # исключаем текущий объект, если редактируется

        if qs.exists():
            # Если такой slug уже есть, добавляем случайный суффикс
            self.slug = f'{base_slug}-{"".join(choices(string.ascii_lowercase + string.digits, k=8))}'

        self.name_lower = self.name.lower() if self.name else ''
        self.article_lower = self.article.lower() if self.article else ''
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=False,
                                related_name='images')
    file = models.ImageField(upload_to='shop/product/images_fixed', blank=True, null=True)
    is_main = models.BooleanField(default=False, null=False)


class Size(models.Model):
    uid = models.CharField(max_length=255, blank=True, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=False,
                                related_name='sizes')
    size = models.CharField('Размер', max_length=20, blank=True, null=True)
    quantity = models.IntegerField('Остаток', blank=True, null=True)
    price = models.DecimalField('Цена', default=0, decimal_places=2, max_digits=7, blank=True, null=True)
    price_init = models.DecimalField('Цена исходная', default=0, decimal_places=2, max_digits=7, blank=True, null=True)
    price_opt = models.DecimalField('Цена оптовая', default=0, decimal_places=2, max_digits=7, blank=True, null=True)
    price_opt_init = models.DecimalField('Цена оптовая исходная', default=0, decimal_places=2, max_digits=7, blank=True, null=True)

    min_weight = models.DecimalField('Минимальный вес', decimal_places=4, max_digits=8, blank=True, null=True)
    max_weight = models.DecimalField('Максимальный вес', decimal_places=4, max_digits=8, blank=True, null=True)
    avg_weight = models.DecimalField('Средний вес', decimal_places=4, max_digits=8, blank=True, null=True)
    selected_amount = models.IntegerField(default=0, null=True, editable=False)

    def __str__(self):
        return f'{self.product.name} - {self.price}'

    class Meta:
        ordering = ('size',)
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'




class Popular(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    uid = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return f'{self.uid}'


    class Meta:
        ordering = ('order_num',)
        verbose_name = 'Популярные товары'
        verbose_name_plural = 'Популярные товары'


class Favorite(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, null=False, blank=False, related_name='favorites')


class Banner(models.Model):
    order_num = models.IntegerField(default=10)
    image_big = ResizedImageField('Фон 1980х650', size=[1980, 650], quality=95, force_format='WEBP', upload_to='banner/images',
                              blank=False, null=True)
    image_small = ResizedImageField('Картинка 670х450', size=[670, 450], quality=95, force_format='WEBP',
                                 upload_to='banner/images',
                                 blank=False, null=True)
    text_big = models.TextField('Текст большой', blank=True, null=True)
    text_small = models.TextField('Текст маленький', blank=True, null=True)
    button_text = models.CharField('Текст на кнопке',max_length=255, blank=True, null=False)
    button_url = models.CharField('Ссылка на кнопке',max_length=255, blank=True, null=False)
    def __str__(self):
        return f'{self.order_num}'



    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'
        ordering = ['order_num']


class Promo(models.Model):
    order_num = models.IntegerField(default=10)
    image = models.FileField(upload_to='shop/promo/', blank=True, null=True)
    col_span = models.IntegerField(default=12)
    name = models.CharField(max_length=255, blank=True, null=False)
    description = CKEditor5Field('Описание', blank=True, null=True, config_name='extends')
    def __str__(self):
        return f'{self.order_num}'



    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['order_num']

class PromoItem(models.Model):
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, null=False, blank=False, related_name='items')
    uid = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return f'{self.uid}'