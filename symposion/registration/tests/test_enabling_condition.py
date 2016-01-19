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

class EnablingConditionTestCases(RegistrationCartTestCase):

    @classmethod
    def add_product_enabling_condition(cls):
        ''' Adds a product enabling condition: adding PROD_1 to a cart is
        predicated on adding PROD_2 beforehand. '''
        enabling_condition = rego.ProductEnablingCondition.objects.create(
            description="Product condition",
            mandatory=False,
        )
        enabling_condition.save()
        enabling_condition.products.add(cls.PROD_1)
        enabling_condition.enabling_products.add(cls.PROD_2)
        enabling_condition.save()


    def test_product_enabling_condition_enables_product(self):
        self.add_product_enabling_condition()

        # Cannot buy PROD_1 without buying PROD_2
        current_cart = CartController.for_user(self.USER_1)
        with self.assertRaises(ValidationError):
            current_cart.add_to_cart(self.PROD_1, 1)

        current_cart.add_to_cart(self.PROD_2, 1)
        current_cart.add_to_cart(self.PROD_1, 1)


    def test_product_enabled_by_previous_cart(self):
        self.add_product_enabling_condition()

        current_cart = CartController.for_user(self.USER_1)
        current_cart.add_to_cart(self.PROD_2, 1)
        current_cart.cart.active = False
        current_cart.cart.save()

        # Create new cart and try to add PROD_1
        current_cart = CartController.for_user(self.USER_1)
        current_cart.add_to_cart(self.PROD_1, 1)
