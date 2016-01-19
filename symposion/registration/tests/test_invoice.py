import datetime
import pytz

from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from symposion.registration import models as rego
from symposion.registration.cart import CartController
from symposion.registration.invoice import InvoiceController

from test_cart import RegistrationCartTestCase

UTC = pytz.timezone('UTC')


class InvoiceTestCase(RegistrationCartTestCase):

    def test_create_invoice(self):
        current_cart = CartController.for_user(self.USER_1)

        # Should be able to create an invoice after the product is added
        current_cart.add_to_cart(self.PROD_1, 1)
        invoice_1 = InvoiceController.for_cart(current_cart.cart)
        invoice_1.invoice

        # Adding item to cart should void all active invoices and produce
        # a new invoice
        current_cart.add_to_cart(self.PROD_1, 1)
        invoice_2 = InvoiceController.for_cart(current_cart.cart)
        self.assertNotEqual(invoice_1.invoice, invoice_2.invoice)


    def test_create_invoice_fails_if_cart_invalid(self):
        pass
