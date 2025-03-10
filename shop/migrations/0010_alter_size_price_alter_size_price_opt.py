# Generated by Django 5.1.1 on 2024-10-16 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_alter_size_price_alter_size_price_opt_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='size',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=7, null=True, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='size',
            name='price_opt',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=7, null=True, verbose_name='Цена оптовая'),
        ),
    ]
