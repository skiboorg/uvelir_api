# Generated by Django 5.1.1 on 2025-03-17 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_cart_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='amount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
