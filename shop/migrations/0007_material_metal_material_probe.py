# Generated by Django 5.1.1 on 2024-10-14 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_material_subcategoryfilter_product_material_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='metal',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Метал'),
        ),
        migrations.AddField(
            model_name='material',
            name='probe',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Проба'),
        ),
    ]
