from __future__ import unicode_literals

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
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
        return "Voucher for %s" % self.recipient

    recipient = models.CharField(max_length=64, verbose_name=_("Recipient"))
    code = models.CharField(max_length=16, verbose_name=_("Voucher code"))
    count = models.PositiveIntegerField(verbose_name=_("Voucher use limit"))


# Product Modifiers

@python_2_unicode_compatible
class DiscountBase(models.Model):
    ''' Base class for discounts. Each subclass has controller code that
    determines whether or not the given discount is available to be added to the
    current cart. '''

    def __str__(self):
        return "Discount: " + self.description

    description = models.CharField(max_length=255,
        verbose_name=_("Description"))
    reuse_limit = models.PositiveIntegerField(
        verbose_name=_("Usage limit per user"))


@python_2_unicode_compatible
class DiscountForProduct(models.Model):
    ''' Represents a discount for an individual product. Each discount can
    contain multiple products. Discounts can either be a percentage or a
    fixed amount, but not both. '''

    def __str__(self):
        if self.percentage:
            return "%s%% off %s" % (self.percentage, self.Product)
        elif self.price:
            return "$%s off %s" % (self.price, self.Product)

    def clean(self):
        if self.percentage is None and self.price is None:
            raise ValidationError(
                _("Discount must have a percentage or a price."))
        elif self.percentage is not None and self.price is not None:
            raise ValidationError(
                _("Discount may only have a percentage or only a price."))

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=4, decimal_places=1, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True)


class LimitedAvailabilityDiscount(DiscountBase):
    ''' Discounts that are generally available, but are limited by timespan or
    usage count. This is for e.g. Early Bird discounts. '''

    start_time = models.DateTimeField(blank=True, verbose_name=_("Start time"))
    end_time = models.DateTimeField(blank=True, verbose_name=_("End time"))
    limit = models.PositiveIntegerField(blank=True, verbose_name=_("Limit"))


class VoucherDiscount(DiscountBase):
    ''' Discounts that are enabled when a voucher code is in the current
    cart. '''

    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE,
        verbose_name=_("Voucher"))


class IncludedProductDiscount(DiscountBase):
    ''' Discounts that are enabled because another product has been purchased.
    e.g. A conference ticket includes a free t-shirt. '''

    product = models.ManyToManyField(Product,
        verbose_name=_("Including product"))


class RoleDiscount(object):
    ''' Discounts that are enabled because the active user has a specific
    role. This is for e.g. volunteers who can get a discount ticket. '''
    ## TODO: implement RoleDiscount
    pass


class EnablingConditionBase(models.Model):
    ''' This defines a condition which allows products or categories to
    be made visible. If there is at least one enabling condition defined
    on a Product or Category, it will only be enabled if at least one
    condition is met. '''

    products = models.ManyToManyField(Product)
    categories = models.ManyToManyField(Category)


@python_2_unicode_compatible
class ProductEnablingCondition(EnablingConditionBase):
    ''' The condition is met because a specific product is purchased. '''

    def __str__(self):
        return "Enabled by product: "

    product = models.ManyToManyField(Product)


@python_2_unicode_compatible
class CategoryEnablingCondition(EnablingConditionBase):
    ''' The condition is met because a product in a particular product is
    purchased. '''

    def __str__(self):
        return "Enabled by product in category: "

    category = models.ForeignKey(Category)


@python_2_unicode_compatible
class VoucherEnablingCondition(EnablingConditionBase):
    ''' The condition is met because a Voucher is present. This is for e.g.
    enabling sponsor tickets. '''

    def __str__(self):
        return "Enabled by voucher: %s" % voucher

    voucher = models.ForeignKey(Voucher)


#@python_2_unicode_compatible
class RoleEnablingCondition(object):
    ''' The condition is met because the active user has a particular Role.
    This is for e.g. enabling Team tickets. '''
    ## TODO: implement RoleEnablingCondition
    pass


# Commerce Models

class Cart(models.Model):
    ''' Represents a set of product items that have been purchased, or are
    pending purchase. '''

    user = models.ForeignKey(User)
    # ProductItems (foreign key)
    vouchers = models.ManyToManyField(Voucher, blank=True)
    discounts = models.ManyToManyField(DiscountBase, blank=True)
    time_last_updated = models.DateTimeField()
    revision = models.PositiveIntegerField()
    active = models.BooleanField(default=True)


class ProductItem(models.Model):
    ''' Represents a product-quantity pair in a Cart. '''

    cart = models.ForeignKey(Cart)
    product = models.ForeignKey(Product)
    quantity = models.PositiveIntegerField()


class Invoice(models.Model):
    ''' An invoice. Invoices can be automatically generated when checking out
    a Cart, in which case, it is attached to a given revision of a Cart. '''

    # Invoice Number
    user = models.ForeignKey(User)
    cart = models.ForeignKey(Cart, blank=True)
    cart_revision = models.IntegerField()
    # Line Items (foreign key)
    void = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)


class LineItem(models.Model):
    ''' Line items for an invoice. These are denormalised from the ProductItems
    that belong to a cart (for consistency), but also allow for arbitrary line
    items when required. '''

    invoice = models.ForeignKey(Invoice)
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)


class Payment(models.Model):
    ''' A payment for an invoice. Each invoice can have multiple payments
    attached to it.'''

    invoice = models.ForeignKey(Invoice)
    time = models.DateTimeField()
    reference = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
