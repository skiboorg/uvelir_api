# Generated by Django 5.1.1 on 2024-11-01 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0015_popular'),
    ]

    operations = [
        migrations.AlterField(
            model_name='size',
            name='uid',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='sizefilter',
            name='size',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Размер'),
        ),
    ]