import datetime

from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from symposion.registration import models as rego
from symposion.registration.cart import CartController

from patch_datetime import SetTimeMixin

class AddToCartTestCase(SetTimeMixin, TestCase):

    def setUp(self):
        super(AddToCartTestCase, self).setUp()

    @classmethod
    def setUpTestData(cls):
        cls.USER_1 = User.objects.create_user(username='testuser',
            email='test@example.com', password='top_secret')

        cls.USER_2 = User.objects.create_user(username='testuser2',
            email='test2@example.com', password='top_secret')

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

        cls.PROD_2 = rego.Product.objects.create(
            name="Product 2",
            description= "This is a test product. It costs $10. " \
                "A user may have 10 of them.",
            category=cls.CAT_1,
            price=Decimal("10.00"),
            limit_per_user=10,
            order=10,
        )
        cls.PROD_2.save()

    def test_get_cart(self):
        current_cart = CartController(self.USER_1)

        current_cart.cart.active = False
        current_cart.cart.save()

        old_cart = current_cart

        current_cart = CartController(self.USER_1)
        self.assertNotEqual(old_cart.cart, current_cart.cart)

        current_cart2 = CartController(self.USER_1)
        self.assertEqual(current_cart.cart, current_cart2.cart)


    def test_add_to_cart_collapses_product_items(self):
        current_cart = CartController(self.USER_1)

        # Add a product twice
        current_cart.add_to_cart(self.PROD_1, 1)
        current_cart.add_to_cart(self.PROD_1, 1)

        ## Count of products for a given user should be collapsed.
        items = rego.ProductItem.objects.filter(cart=current_cart.cart,
            product=self.PROD_1)
        self.assertEqual(1, len(items))
        item = items[0]
        self.assertEquals(2, item.quantity)


    def test_add_to_cart_per_user_limit(self):
        current_cart = CartController(self.USER_1)

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

        current_cart = CartController(self.USER_1)
        # User should not be able to add 10 of PROD_1 to the current cart now,
        # even though it's a new cart.
        try:
            current_cart.add_to_cart(self.PROD_1, 10)
        except ValidationError:
            pass
        else:
            raise AssertionError("Was able to exceed per-user limit over multiple carts")


    def test_add_to_cart_ceiling_limit(self):

        limit_ceiling = rego.TimeOrStockLimitEnablingCondition.objects.create(
            description="Ceiling 1",
            mandatory=True,
            limit=9,
        )
        limit_ceiling.save()
        limit_ceiling.products.add(self.PROD_1, self.PROD_2)
        limit_ceiling.save()

        current_cart = CartController(self.USER_1)

        # User should not be able to add 10 of PROD_1 to the current cart
        # because it is affected by CEIL_1
        try:
            current_cart.add_to_cart(self.PROD_2, 10)
        except ValidationError:
            pass
        else:
            raise AssertionError("Was able to exceed ceiling limit over single product")

        # User should be able to add 5 of PROD_1 to the current cart
        current_cart.add_to_cart(self.PROD_1, 5)

        # User should not be able to add 10 of PROD_2 to the current cart
        # because it is affected by CEIL_1
        try:
            current_cart.add_to_cart(self.PROD_2, 10)
        except ValidationError:
            pass
        else:
            raise AssertionError("Was able to exceed ceiling limit over multiple products")

        # User should be able to add 5 of PROD_2 to the current cart
        current_cart.add_to_cart(self.PROD_2, 4)
