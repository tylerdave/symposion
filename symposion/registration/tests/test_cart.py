from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from symposion.registration import models as rego

from symposion.registration.cart import CartController

class AddToCartTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
        username='testuser', email='test@example.com', password='top_secret')

    @classmethod
    def setUpTestData(cls):
        cls.CAT_1 = rego.Category.objects.create(
            name="Category 1",
            description="This is a test category",
            order=10,
            render_type=rego.Category.RENDER_TYPE_RADIO,
        )
        cls.CAT_1.save()

        cls.PROD_1 = rego.Product.objects.create(
            name="Product 1",
            description= "This is a test product. It costs $10. " \
                "A user may have 10 of them.",
            category=cls.CAT_1,
            price=Decimal("10.00"),
            limit_per_user=10,
            order=10,
        )
        cls.PROD_1.save()


    def test_get_cart(self):
        current_cart = CartController(self.user)

        current_cart.cart.active = False
        current_cart.cart.save()

        old_cart = current_cart

        current_cart = CartController(self.user)
        self.assertNotEqual(old_cart.cart, current_cart.cart)

        current_cart2 = CartController(self.user)
        self.assertEqual(current_cart.cart, current_cart2.cart)


    def test_add_to_cart_per_user_limit(self):
        current_cart = CartController(self.user)

        # User should be able to add 1 of PROD_1 to the current cart.
        current_cart.add_to_cart(self.PROD_1, 1)

        # User should be able to add 1 of PROD_1 to the current cart.
        current_cart.add_to_cart(self.PROD_1, 1)

        # User should not be able to add 10 of PROD_1 to the current cart now,
        # because they have a limit of 10.
        try:
            current_cart.add_to_cart(self.PROD_1, 10)
        except ValidationError:
            pass
        else:
            raise AssertionError("Was able to exceed per-user limit on one cart")

        current_cart.cart.active = False
        current_cart.cart.save()

        current_cart = CartController(self.user)
        # User should not be able to add 10 of PROD_1 to the current cart now,
        # even though it's a new cart.
        try:
            current_cart.add_to_cart(self.PROD_1, 10)
        except ValidationError:
            pass
        else:
            raise AssertionError("Was able to exceed per-user limit over multiple carts")
