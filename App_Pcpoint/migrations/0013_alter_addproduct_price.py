# Generated by Django 4.0.1 on 2022-02-03 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_Pcpoint', '0012_alter_carts_price_alter_carts_totalprice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addproduct',
            name='price',
            field=models.IntegerField(default=1),
        ),
    ]
