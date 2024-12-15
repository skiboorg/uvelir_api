from django.db import models
from pytils.translit import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django_resized import ResizedImageField
from random import choices
import string


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
    value = models.CharField('ЧПУ', max_length=255, blank=True, null=True)
    def save(self, *args, **kwargs):

        self.value = slugify(self.label)
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

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('order_num',)
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'




class Product(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False)
    article = models.CharField('Артикул',max_length=100,blank=True, null=True)
    subcategory = models.ForeignKey(SubCategory,blank=True,null=True,on_delete=models.CASCADE, related_name='products')
    coating = models.ForeignKey(Coating,blank=True,null=True,on_delete=models.CASCADE, related_name='Покрытие')
    fineness = models.ForeignKey(Fineness,blank=True,null=True,on_delete=models.CASCADE, related_name='Вставка')
    material = models.ForeignKey(Material,blank=True,null=True,on_delete=models.CASCADE, related_name='Материал')
    filter = models.ForeignKey(SubCategoryFilter,blank=True,null=True,on_delete=models.CASCADE, related_name='Фильтр')
    is_new = models.BooleanField('Новинка', default=False, null=False)
    is_popular = models.BooleanField('Популярный', default=False, null=False)
    is_active = models.BooleanField('Отображать?', default=True, null=False)
    is_in_stock = models.BooleanField('В наличии?', default=True, null=False)
    not_image = models.BooleanField(default=False, null=False)
    image = models.ImageField(upload_to='shop/product/images_fixed', blank=True, null=True)

    name = models.CharField('Название', max_length=255, blank=False, null=True)
    slug = models.CharField('ЧПУ',max_length=255,
                            help_text='Если не заполнено, создается на основе поля Назавание',
                            blank=True, null=True, editable=False)
    short_description = models.TextField('Короткое описание', blank=True, null=False)
    description = CKEditor5Field('Описание', blank=True, null=True, config_name='extends')
    items_count = models.IntegerField('Кол-во товаров', default=0, null=True)
    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ('-image',)
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def save(self, *args, **kwargs):

        self.slug = f'{slugify(self.name)}-{"".join(choices(string.ascii_lowercase + string.digits, k=8))}'
        super().save(*args, **kwargs)



class Size(models.Model):
    uid = models.CharField(max_length=255, blank=True, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=False,
                                related_name='sizes')
    size = models.CharField('Размер', max_length=20, blank=True, null=True)
    quantity = models.IntegerField('Остаток', blank=True, null=True)
    price = models.DecimalField('Цена', default=0, decimal_places=2, max_digits=7, blank=True, null=True)
    price_opt = models.DecimalField('Цена оптовая', default=0, decimal_places=2, max_digits=7, blank=True, null=True)

    min_weight = models.DecimalField('Минимальный вес', decimal_places=4, max_digits=8, blank=True, null=True)
    max_weight = models.DecimalField('Максимальный вес', decimal_places=4, max_digits=8, blank=True, null=True)
    avg_weight = models.DecimalField('Средний вес', decimal_places=4, max_digits=8, blank=True, null=True)
    selected_amount = models.IntegerField(default=0, null=True, editable=False)

    def __str__(self):
        return f'{self.product.name} - {self.price}'

    class Meta:
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