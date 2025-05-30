# Generated by Django 5.1.1 on 2025-04-01 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0027_banner'),
    ]

    operations = [
        migrations.AddField(
            model_name='fineness',
            name='label_lower',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='product',
            name='article_lower',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Артикул'),
        ),
        migrations.AddField(
            model_name='product',
            name='garniture_set_uuids',
            field=models.TextField(blank=True, null=True),
        ),
    ]
