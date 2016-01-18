from django.core.exceptions import ObjectDoesNotExist

from django.utils import timezone

from symposion.registration import models as rego

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
