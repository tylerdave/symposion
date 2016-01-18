from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError

from django.utils import timezone

from symposion.registration import models as rego

from controllers import ProductController

class CartController(object):

    def __init__(self, user):
        self.cart = self._cart_for_user(user)

    def _cart_for_user(self, user):
        ''' Returns the user's current cart, or creates a new cart
        if there isn't one ready yet. '''

        try:
            existing = rego.Cart.objects.get(user=user, active=True)
        except ObjectDoesNotExist:
            existing = rego.Cart.objects.create(
                user=user,
                time_last_updated=timezone.now() )
            existing.save()
        return existing

    def _update_time_last_updated(self):
        ''' Updates the cart's time last updated value, which is used to
        determine whether the cart has reserved the items and discounts it
        holds. '''
        self.cart.time_last_updated = timezone.now()

    def add_to_cart(self, product, quantity):
        ''' Adds _quantity_ of the given _product_ to the cart. Raises
        ValidationError if constraints are violated.'''

        prod = ProductController(product)

        # TODO: Check enabling conditions for product for user

        if not prod.can_add_within_ceilings(quantity):
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

        self._update_time_last_updated()
        self.cart.save()
