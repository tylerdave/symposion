# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('symposion_registration', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='voucher',
            old_name='count',
            new_name='limit',
        ),
        migrations.AlterField(
            model_name='voucher',
            name='code',
            field=models.CharField(unique=True, max_length=16, verbose_name='Voucher code'),
        ),
    ]
