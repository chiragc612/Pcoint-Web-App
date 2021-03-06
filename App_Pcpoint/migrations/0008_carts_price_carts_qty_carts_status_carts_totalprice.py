# Generated by Django 4.0.1 on 2022-02-03 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_Pcpoint', '0007_carts'),
    ]

    operations = [
        migrations.AddField(
            model_name='carts',
            name='price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='carts',
            name='qty',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='carts',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='carts',
            name='totalprice',
            field=models.IntegerField(default=0),
        ),
    ]
