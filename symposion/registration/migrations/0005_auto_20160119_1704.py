# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('symposion_registration', '0004_auto_20160119_0443'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='cart',
            name='discounts',
        ),
        migrations.AlterField(
            model_name='discountforproduct',
            name='percentage',
            field=models.DecimalField(null=True, max_digits=4, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='discountforproduct',
            name='price',
            field=models.DecimalField(null=True, max_digits=8, decimal_places=2),
        ),
        migrations.AddField(
            model_name='discountitem',
            name='cart',
            field=models.ForeignKey(to='symposion_registration.Cart'),
        ),
        migrations.AddField(
            model_name='discountitem',
            name='discount',
            field=models.ForeignKey(to='symposion_registration.DiscountBase'),
        ),
        migrations.AddField(
            model_name='discountitem',
            name='product',
            field=models.ForeignKey(to='symposion_registration.Product'),
        ),
    ]
