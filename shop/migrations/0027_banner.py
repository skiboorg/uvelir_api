# Generated by Django 5.1.1 on 2025-02-26 06:36

import django_resized.forms
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0026_rename_image_productimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_num', models.IntegerField(default=10)),
                ('image_big', django_resized.forms.ResizedImageField(crop=None, force_format='WEBP', keep_meta=True, null=True, quality=95, scale=None, size=[1980, 650], upload_to='banner/images', verbose_name='Фон 1980х650')),
                ('image_small', django_resized.forms.ResizedImageField(crop=None, force_format='WEBP', keep_meta=True, null=True, quality=95, scale=None, size=[670, 450], upload_to='banner/images', verbose_name='Картинка 670х450')),
                ('text_big', models.TextField(blank=True, null=True, verbose_name='Текст большой')),
                ('text_small', models.TextField(blank=True, null=True, verbose_name='Текст маленький')),
                ('button_text', models.CharField(blank=True, max_length=255, verbose_name='Текст на кнопке')),
                ('button_url', models.CharField(blank=True, max_length=255, verbose_name='Ссылка на кнопке')),
            ],
            options={
                'verbose_name': 'Баннер',
                'verbose_name_plural': 'Баннеры',
                'ordering': ['order_num'],
            },
        ),
    ]
