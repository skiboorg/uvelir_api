# Generated by Django 5.1.1 on 2024-10-22 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_alter_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Отображать?'),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Отображать?'),
        ),
    ]