# Generated by Django 5.1.1 on 2024-10-14 16:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_rename_name_coating_label_rename_slug_coating_value_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255, verbose_name='Название')),
                ('value', models.CharField(blank=True, max_length=255, null=True, verbose_name='ЧПУ')),
            ],
            options={
                'verbose_name': 'Материал',
                'verbose_name_plural': 'Материалы',
            },
        ),
        migrations.CreateModel(
            name='SubCategoryFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('slug', models.CharField(blank=True, max_length=255, null=True, verbose_name='ЧПУ')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Материал', to='shop.material'),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='filters',
            field=models.ManyToManyField(blank=True, to='shop.subcategoryfilter'),
        ),
    ]
