# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('symposion_registration', '0003_auto_20160119_0421'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categoryenablingcondition',
            old_name='enabling_categories',
            new_name='enabling_category',
        ),
    ]
