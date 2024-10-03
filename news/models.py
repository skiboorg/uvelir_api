from django.db import models
from pytils.translit import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django_resized import ResizedImageField

class Tag(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    name = models.CharField('Название', max_length=255, blank=False, null=False)
    slug = models.CharField('ЧПУ', max_length=255,
                            help_text='Если не заполнено, создается на основе поля Назавание',
                            blank=True, null=True, editable=False)

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('order_num',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class NewsItem(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    tag = models.ForeignKey(Tag,blank=True,null=True,on_delete=models.CASCADE,related_name='Тег')
    image = ResizedImageField('Картинка превью',size=[470, 315], quality=95, force_format='WEBP', upload_to='news/images',
                              blank=False, null=True)
    image_top = ResizedImageField('Картинка вверху статьи (1080x450)', size=[1080, 450], quality=95, force_format='WEBP',
                              upload_to='news/images',
                              blank=False, null=True)

    name = models.CharField('Название', max_length=255, blank=False, null=True)
    slug = models.CharField('ЧПУ',max_length=255,
                            help_text='Если не заполнено, создается на основе поля Назавание',
                            blank=True, null=True, editable=False)
    time_to_read = models.CharField('Время чтения', max_length=255, blank=True, null=True)
    description = models.TextField('Короткое описание', blank=True, null=True)
    html_content = CKEditor5Field('Контент', blank=True, null=False, config_name='extends')

    created = models.DateField(auto_now_add=True)
    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ('order_num',)
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ContentBlockType(models.Model):
    name = models.CharField(max_length=255, blank=False,null=True)
    slug = models.CharField('ЧПУ', max_length=255,blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Тип контент блок'
        verbose_name_plural = 'Типы контент блоков'


class ContentBlock(models.Model):
    order_num = models.IntegerField(default=1, null=True)
    type = models.ForeignKey(ContentBlockType, on_delete=models.CASCADE, null=True, blank=False)
    product = models.ForeignKey(NewsItem, on_delete=models.CASCADE, null=True, blank=False,
                                related_name='content_blocks')
    image = ResizedImageField('Картинка с текстом',size=[520, 400], quality=95, force_format='WEBP', upload_to='news/images',
                              blank=True, null=True)
    image_big = ResizedImageField('Одиночная картинка', size=[1440, 500], quality=95, force_format='WEBP',
                             upload_to='news/images',
                             blank=True, null=True)
    html_content1 = CKEditor5Field('Текстовый блок1', blank=True, null=False, config_name='extends')
    html_content2 = CKEditor5Field('Текстовый блок2', blank=True, null=False, config_name='extends')

    def __str__(self):
        return f''

    class Meta:
        ordering = ('order_num',)
        verbose_name = 'Контент блок'
        verbose_name_plural = 'Контент блоки'


