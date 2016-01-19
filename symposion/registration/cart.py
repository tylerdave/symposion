import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db.models import Avg, Min, Max
from django.utils import timezone

from symposion.registration import models as rego

from controllers import ProductController

class CartController(object):

    def __init__(self, cart):
        self.cart = cart

    @staticmethod
    def for_user(user):
        ''' Returns the user's current cart, or creates a new cart
        if there isn't one ready yet. '''

        try:
            existing = rego.Cart.objects.get(user=user, active=True)
        except ObjectDoesNotExist:
            existing = rego.Cart.objects.create(
                user=user,
                time_last_updated=timezone.now(),
                reservation_duration=datetime.timedelta(),
                 )
            existing.save()
        return CartController(existing)


    def extend_reservation(self):
        ''' Updates the cart's time last updated value, which is used to
        determine whether the cart has reserved the items and discounts it
        holds. '''

        reservations = [datetime.timedelta()]

        # If we have vouchers, we're entitled to an hour at minimum.
        if len(self.cart.vouchers.all()) >= 1:
            reservations.append(rego.Voucher.RESERVATION_DURATION)

        # Else, it's the maximum of the included products
        items = rego.ProductItem.objects.filter(cart=self.cart)
        agg = items.aggregate(Max("product__reservation_duration"))
        product_max = agg["product__reservation_duration__max"]

        if product_max is not None:
            reservations.append(product_max)

        self.cart.time_last_updated = timezone.now()
        self.cart.reservation_duration = max(reservations)


    def add_to_cart(self, product, quantity):
        ''' Adds _quantity_ of the given _product_ to the cart. Raises
        ValidationError if constraints are violated.'''

        prod = ProductController(product)

        # TODO: Check enabling conditions for product for user

        if not prod.can_add_with_enabling_conditions(self.cart.user, quantity):
                raise ValidationError("Not enough of that product left")

        if not prod.user_can_add_within_limit(self.cart.user, quantity):
            raise ValidationError("Not enough of that product left")

        try:
            # Try to update an existing item within this cart if possible.
            product_item = rego.ProductItem.objects.get(
                cart=self.cart,
                product=product)
            product_item.quantity += quantity
        except ObjectDoesNotExist:
            product_item = rego.ProductItem.objects.create(
                cart=self.cart,
                product=product,
                quantity=quantity,
            )
        product_item.save()

        # TODO: Calculate discounts

        self.extend_reservation()
        self.cart.revision += 1
        self.cart.save()


    def apply_voucher(self, voucher):
        ''' Applies the given voucher to this cart. '''

        # TODO: is it valid for a cart to re-add a voucher that they have?

        # Is voucher exhausted?
        active_carts = rego.Cart.reserved_carts()
        carts_with_voucher = active_carts.filter(vouchers=voucher)
        if len(carts_with_voucher) >= voucher.limit:
            raise ValidationError("This voucher is no longer available")

        # If successful...
        self.cart.vouchers.add(voucher)

        self.extend_reservation()
        self.cart.revision += 1
        self.cart.save()


    def validate_cart(self):
        ''' Determines whether the status of the current cart is valid;
        this is normally called before generating or paying an invoice '''

        is_reserved = self.cart in rego.Cart.reserved_carts()

        # TODO: validate vouchers

        items = rego.ProductItem.objects.filter(cart=self.cart)
        for item in items:
            # per-user limits are tested at add time, and are unliklely to change
            prod = ProductController(item.product)

            # If the cart is not reserved, we need to see if we can re-reserve
            quantity = 0 if is_reserved else item.quantity

            if not prod.can_add_with_enabling_conditions(self.cart.user, quantity):
                raise ValidationError("Products are no longer available")

        # TODO: recalculate discounts
