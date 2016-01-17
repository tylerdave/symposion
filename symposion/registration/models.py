from __future__ import unicode_literals

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from symposion.markdown_parser import parse
from symposion.proposals.models import ProposalBase



# Inventory Models

@python_2_unicode_compatible
class Category(models.Model):
    ''' Registration product categories '''

    def __str__(self):
        return self.name

    RENDER_TYPE_RADIO = 1
    RENDER_TYPE_QUANTITY = 2

    CATEGORY_RENDER_TYPES = [
        (RENDER_TYPE_RADIO, _("Radio button")),
        (RENDER_TYPE_QUANTITY, _("Quantity boxes")),
    ]

    name = models.CharField(max_length=65, verbose_name=_("Name"))
    description = models.CharField(max_length=255, verbose_name=_("Description"))
    order = models.PositiveIntegerField(verbose_name=("Display order"))
    render_type = models.IntegerField(choices=CATEGORY_RENDER_TYPES, verbose_name=_("Render type"))


@python_2_unicode_compatible
class Ceiling(models.Model):
    ''' Registration product ceilings '''

    def __str__(self):
        return self.name

    name = models.CharField(max_length=32, verbose_name=_("Ceiling name"))
    start_time = models.DateTimeField(blank=True, verbose_name=_("Start time"))
    end_time = models.DateTimeField(blank=True, verbose_name=_("End time"))
    limit = models.PositiveIntegerField(blank=True, verbose_name=_("Limit"))


@python_2_unicode_compatible
class Product(models.Model):
    ''' Registration products '''

    def __str__(self):
        return self.name

    name = models.CharField(max_length=65, verbose_name=_("Name"))
    description = models.CharField(max_length=255, verbose_name=_("Description"))
    category = models.ForeignKey(Category, verbose_name=_("Product category"))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price"))
    limit_per_user = models.PositiveIntegerField(blank=True, verbose_name=_("Limit per user"))
    reservation_duration = models.DurationField(verbose_name=_("Reservation duration"))
    order = models.PositiveIntegerField(verbose_name=("Display order"))
    ceilings = models.ManyToManyField(Ceiling, blank=True, verbose_name=("Product ceilings"))


@python_2_unicode_compatible
class Voucher(models.Model):
    ''' Registration vouchers '''

    def __str__(self):
        return "Voucher: %s" % self.description

    description = models.CharField(max_length=255, verbose_name=_("Description"))
    code = models.CharField(max_length=16, verbose_name=_("Voucher code"))
    count = models.PositiveIntegerField(verbose_name=_("Voucher use limit"))
