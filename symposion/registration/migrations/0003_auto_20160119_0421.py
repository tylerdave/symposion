# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('symposion_registration', '0002_auto_20160119_0133'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categoryenablingcondition',
            old_name='category',
            new_name='enabling_categories',
        ),
        migrations.RenameField(
            model_name='includedproductdiscount',
            old_name='product',
            new_name='enabling_products',
        ),
        migrations.RenameField(
            model_name='productenablingcondition',
            old_name='product',
            new_name='enabling_products',
        ),
        migrations.AlterField(
            model_name='payment',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
