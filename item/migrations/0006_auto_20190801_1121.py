# Generated by Django 2.2.3 on 2019-08-01 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0005_item_cate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='cate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='item.Categories'),
        ),
    ]
