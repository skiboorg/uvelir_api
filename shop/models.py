from django.db import models
from pytils.translit import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django_resized import ResizedImageField


class Category(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    uid = models.CharField(max_length=255, blank=False, null=False)
    image = ResizedImageField(size=[420, 420], quality=95, force_format='WEBP', upload_to='shop/category/images',
                              blank=True, null=True)
    name = models.CharField('Название', max_length=255, blank=False, null=False)
    slug = models.CharField('ЧПУ', max_length=255,blank=True, null=True)
    short_description = models.TextField('Короткое описание', blank=True, null=False)
    html_content = CKEditor5Field('SEO текст', blank=True, null=False)
    items_count = models.IntegerField('Кол-во товаров', default=0, null=True)
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
    product = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=False,
                                related_name='size_filters')
    size = models.DecimalField('Размер', decimal_places=2, max_digits=8, blank=True, null=True)

class SubCategory(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    uid = models.CharField(max_length=255, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, null=True, related_name='sub_categories')
    name = models.CharField('Название', max_length=255, blank=False, null=False)
    slug = models.CharField('ЧПУ', max_length=255,blank=True, null=True)
    image = ResizedImageField(size=[420, 420], quality=95, force_format='WEBP', upload_to='shop/category/images',
                              blank=True, null=True)
    short_description = models.TextField('Короткое описание', blank=True, null=False)
    html_content = CKEditor5Field('SEO текст', blank=True, null=False)
    items_count = models.IntegerField('Кол-во товаров', default=0, null=True)

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):

        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('order_num',)
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'


class Fineness(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField('Название', max_length=255, blank=False, null=False)
    slug = models.CharField('ЧПУ', max_length=255, blank=True, null=True)
    def save(self, *args, **kwargs):

        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:

        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'


class Coating(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField('Название', max_length=255, blank=False, null=False)
    slug = models.CharField('ЧПУ', max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Вставка'
        verbose_name_plural = 'Вставки'


class Product(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False)
    article = models.CharField('Артикул',max_length=20,blank=True, null=True)
    subcategory = models.ForeignKey(SubCategory,blank=True,null=True,on_delete=models.CASCADE, related_name='products')
    coating = models.ForeignKey(Coating,blank=True,null=True,on_delete=models.CASCADE)
    fineness = models.ForeignKey(Fineness,blank=True,null=True,on_delete=models.CASCADE)
    is_new = models.BooleanField('Новинка', default=False, null=False)
    is_popular = models.BooleanField('Популярный', default=False, null=False)
    is_active = models.BooleanField('Отображать?', default=True, null=False)
    is_in_stock = models.BooleanField('В наличии?', default=True, null=False)
    image = ResizedImageField(size=[800, 600], quality=95, force_format='WEBP', upload_to='shop/product/images',
                              blank=False, null=True)

    name = models.CharField('Название', max_length=255, blank=False, null=True)
    slug = models.CharField('ЧПУ',max_length=255,
                            help_text='Если не заполнено, создается на основе поля Назавание',
                            blank=True, null=True, editable=False)
    short_description = models.TextField('Короткое описание', blank=True, null=False)
    description = CKEditor5Field('Описание', blank=True, null=True, config_name='extends')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        # ordering = ('order_num',)
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class Size(models.Model):
    uid = models.CharField(max_length=255, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=False,
                                related_name='sizes')
    size = models.DecimalField('Размер', decimal_places=2, max_digits=8, blank=True, null=True)
    quantity = models.IntegerField('Остаток', blank=True, null=True)
    price = models.DecimalField('Цена', decimal_places=2, max_digits=8, blank=True, null=True)
    price_opt = models.DecimalField('Цена оптовая', decimal_places=2, max_digits=8, blank=True, null=True)
    min_weight = models.DecimalField('Минимальный вес', decimal_places=4, max_digits=8, blank=True, null=True)
    max_weight = models.DecimalField('Максимальный вес', decimal_places=4, max_digits=8, blank=True, null=True)
    avg_weight = models.DecimalField('Средний вес', decimal_places=4, max_digits=8, blank=True, null=True)
    selected_amount = models.IntegerField(default=0, null=True, editable=False)

    def __str__(self):
        return f'{self.product.name} - {self.price}'

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'


