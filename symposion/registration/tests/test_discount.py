import datetime
import pytz

from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from symposion.registration import models as rego
from symposion.registration.cart import CartController

from test_cart import RegistrationCartTestCase

UTC = pytz.timezone('UTC')

class DiscountTestCase(RegistrationCartTestCase):

    @classmethod
    def add_discount_prod_1_includes_prod_2(cls):
        discount = rego.IncludedProductDiscount.objects.create(
            description="PROD_1 includes PROD_2",
        )
        discount.save()
        discount.enabling_products.add(cls.PROD_1)
        discount.save()
        rego.DiscountForProduct.objects.create(
            discount=discount,
            product=cls.PROD_2,
            percentage=Decimal(100),
            quantity=1
        ).save()
        return discount


    def test_discount_is_applied(self):
        discount = self.add_discount_prod_1_includes_prod_2()

        cart = CartController.for_user(self.USER_1)
        cart.add_to_cart(self.PROD_1, 1)
        cart.add_to_cart(self.PROD_2, 1)

        # Discounts should be applied at this point...
        self.assertEqual(1, len(cart.cart.discountitem_set.all()))
