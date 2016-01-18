from django.contrib.auth.models import User
from django.test import TestCase

from symposion.registration import models as rego

from symposion.registration.cart import CartController

class AddToCartTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
        username='testuser', email='test@example.com', password='top_secret')

    @classmethod
    def setUpTestData(cls):
        pass

    def test_get_cart(self):
        current_cart = CartController(self.user)

        current_cart.cart.active = False
        current_cart.cart.save()

        old_cart = current_cart

        current_cart = CartController(self.user)
        self.assertNotEqual(old_cart.cart, current_cart.cart)

        current_cart2 = CartController(self.user)
        self.assertEqual(current_cart.cart, current_cart2.cart)
