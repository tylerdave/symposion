# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('company', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_last_updated', models.DateTimeField()),
                ('reservation_duration', models.DurationField()),
                ('revision', models.PositiveIntegerField(default=1)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=65, verbose_name='Name')),
                ('description', models.CharField(max_length=255, verbose_name='Description')),
                ('order', models.PositiveIntegerField(verbose_name='Display order')),
                ('render_type', models.IntegerField(verbose_name='Render type', choices=[(1, 'Radio button'), (2, 'Quantity boxes')])),
            ],
        ),
        migrations.CreateModel(
            name='DiscountBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255, verbose_name='Description')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountForCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.DecimalField(max_digits=4, decimal_places=1, blank=True)),
                ('quantity', models.PositiveIntegerField()),
                ('category', models.ForeignKey(to='symposion_registration.Category')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountForProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.DecimalField(max_digits=4, decimal_places=1, blank=True)),
                ('price', models.DecimalField(max_digits=8, decimal_places=2, blank=True)),
                ('quantity', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EnablingConditionBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('mandatory', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cart_revision', models.IntegerField(null=True)),
                ('void', models.BooleanField(default=False)),
                ('paid', models.BooleanField(default=False)),
                ('value', models.DecimalField(max_digits=8, decimal_places=2)),
                ('cart', models.ForeignKey(to='symposion_registration.Cart', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(max_digits=8, decimal_places=2)),
                ('invoice', models.ForeignKey(to='symposion_registration.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('reference', models.CharField(max_length=64)),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2)),
                ('invoice', models.ForeignKey(to='symposion_registration.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=65, verbose_name='Name')),
                ('description', models.CharField(max_length=255, verbose_name='Description')),
                ('price', models.DecimalField(verbose_name='Price', max_digits=8, decimal_places=2)),
                ('limit_per_user', models.PositiveIntegerField(verbose_name='Limit per user', blank=True)),
                ('reservation_duration', models.DurationField(default=datetime.timedelta(0, 3600), verbose_name='Reservation duration')),
                ('order', models.PositiveIntegerField(verbose_name='Display order')),
                ('category', models.ForeignKey(verbose_name='Product category', to='symposion_registration.Category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField()),
                ('cart', models.ForeignKey(to='symposion_registration.Cart')),
                ('product', models.ForeignKey(to='symposion_registration.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('completed_registration', models.BooleanField(default=False)),
                ('highest_complete_category', models.IntegerField(default=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recipient', models.CharField(max_length=64, verbose_name='Recipient')),
                ('code', models.CharField(max_length=16, verbose_name='Voucher code')),
                ('count', models.PositiveIntegerField(verbose_name='Voucher use limit')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryEnablingCondition',
            fields=[
                ('enablingconditionbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='symposion_registration.EnablingConditionBase')),
                ('category', models.ForeignKey(to='symposion_registration.Category')),
            ],
            bases=('symposion_registration.enablingconditionbase',),
        ),
        migrations.CreateModel(
            name='IncludedProductDiscount',
            fields=[
                ('discountbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='symposion_registration.DiscountBase')),
                ('product', models.ManyToManyField(to='symposion_registration.Product', verbose_name='Including product')),
            ],
            options={
                'verbose_name': 'Product inclusion',
            },
            bases=('symposion_registration.discountbase',),
        ),
        migrations.CreateModel(
            name='ProductEnablingCondition',
            fields=[
                ('enablingconditionbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='symposion_registration.EnablingConditionBase')),
                ('product', models.ManyToManyField(to='symposion_registration.Product')),
            ],
            bases=('symposion_registration.enablingconditionbase',),
        ),
        migrations.CreateModel(
            name='TimeOrStockLimitDiscount',
            fields=[
                ('discountbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='symposion_registration.DiscountBase')),
                ('start_time', models.DateTimeField(null=True, verbose_name='Start time')),
                ('end_time', models.DateTimeField(null=True, verbose_name='End time')),
                ('limit', models.PositiveIntegerField(null=True, verbose_name='Limit')),
            ],
            options={
                'verbose_name': 'Promotional discount',
            },
            bases=('symposion_registration.discountbase',),
        ),
        migrations.CreateModel(
            name='TimeOrStockLimitEnablingCondition',
            fields=[
                ('enablingconditionbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='symposion_registration.EnablingConditionBase')),
                ('start_time', models.DateTimeField(null=True, verbose_name='Start time')),
                ('end_time', models.DateTimeField(null=True, verbose_name='End time')),
                ('limit', models.PositiveIntegerField(null=True, verbose_name='Limit')),
            ],
            bases=('symposion_registration.enablingconditionbase',),
        ),
        migrations.CreateModel(
            name='VoucherDiscount',
            fields=[
                ('discountbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='symposion_registration.DiscountBase')),
                ('voucher', models.OneToOneField(verbose_name='Voucher', to='symposion_registration.Voucher')),
            ],
            bases=('symposion_registration.discountbase',),
        ),
        migrations.CreateModel(
            name='VoucherEnablingCondition',
            fields=[
                ('enablingconditionbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='symposion_registration.EnablingConditionBase')),
                ('voucher', models.OneToOneField(to='symposion_registration.Voucher')),
            ],
            bases=('symposion_registration.enablingconditionbase',),
        ),
        migrations.AddField(
            model_name='enablingconditionbase',
            name='categories',
            field=models.ManyToManyField(to='symposion_registration.Category'),
        ),
        migrations.AddField(
            model_name='enablingconditionbase',
            name='products',
            field=models.ManyToManyField(to='symposion_registration.Product'),
        ),
        migrations.AddField(
            model_name='discountforproduct',
            name='discount',
            field=models.ForeignKey(to='symposion_registration.DiscountBase'),
        ),
        migrations.AddField(
            model_name='discountforproduct',
            name='product',
            field=models.ForeignKey(to='symposion_registration.Product'),
        ),
        migrations.AddField(
            model_name='discountforcategory',
            name='discount',
            field=models.ForeignKey(to='symposion_registration.DiscountBase'),
        ),
        migrations.AddField(
            model_name='cart',
            name='discounts',
            field=models.ManyToManyField(to='symposion_registration.DiscountBase', blank=True),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cart',
            name='vouchers',
            field=models.ManyToManyField(to='symposion_registration.Voucher', blank=True),
        ),
        migrations.AddField(
            model_name='badge',
            name='profile',
            field=models.OneToOneField(to='symposion_registration.Profile'),
        ),
    ]
