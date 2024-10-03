# Generated by Django 5.1.1 on 2024-09-30 08:25

import django.db.models.deletion
import django_ckeditor_5.fields
import django_resized.forms
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContentBlockType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('slug', models.CharField(blank=True, max_length=255, null=True, verbose_name='ЧПУ')),
            ],
            options={
                'verbose_name': 'Тип контент блок',
                'verbose_name_plural': 'Типы контент блоков',
            },
        ),
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_num', models.IntegerField(default=1, null=True)),
                ('image', django_resized.forms.ResizedImageField(crop=None, force_format='WEBP', keep_meta=True, null=True, quality=95, scale=None, size=[470, 315], upload_to='news/images', verbose_name='Картинка превью')),
                ('image_top', django_resized.forms.ResizedImageField(crop=None, force_format='WEBP', keep_meta=True, null=True, quality=95, scale=None, size=[1080, 450], upload_to='news/images', verbose_name='Картинка вверху статьи (1080x450)')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Название')),
                ('slug', models.CharField(blank=True, editable=False, help_text='Если не заполнено, создается на основе поля Назавание', max_length=255, null=True, verbose_name='ЧПУ')),
                ('time_to_read', models.CharField(blank=True, max_length=255, null=True, verbose_name='Время чтения')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Короткое описание')),
                ('html_content', django_ckeditor_5.fields.CKEditor5Field(blank=True, verbose_name='Контент')),
                ('created', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Новость',
                'verbose_name_plural': 'Новости',
                'ordering': ('order_num',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_num', models.IntegerField(default=1, null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('slug', models.CharField(blank=True, editable=False, help_text='Если не заполнено, создается на основе поля Назавание', max_length=255, null=True, verbose_name='ЧПУ')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('order_num',),
            },
        ),
        migrations.CreateModel(
            name='ContentBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_num', models.IntegerField(default=1, null=True)),
                ('image', django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='WEBP', keep_meta=True, null=True, quality=95, scale=None, size=[520, 400], upload_to='news/images', verbose_name='Картинка с текстом')),
                ('image_big', django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='WEBP', keep_meta=True, null=True, quality=95, scale=None, size=[1440, 500], upload_to='news/images', verbose_name='Одиночная картинка')),
                ('html_content1', django_ckeditor_5.fields.CKEditor5Field(blank=True, verbose_name='Текстовый блок1')),
                ('html_content2', django_ckeditor_5.fields.CKEditor5Field(blank=True, verbose_name='Текстовый блок2')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='news.contentblocktype')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content_blocks', to='news.newsitem')),
            ],
            options={
                'verbose_name': 'Контент блок',
                'verbose_name_plural': 'Контент блоки',
                'ordering': ('order_num',),
            },
        ),
        migrations.AddField(
            model_name='newsitem',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Тег', to='news.tag'),
        ),
    ]
