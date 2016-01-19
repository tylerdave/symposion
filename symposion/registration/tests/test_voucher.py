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


class VoucherTestCases(RegistrationCartTestCase):

    def test_apply_voucher(self):
        voucher = rego.Voucher.objects.create(
            recipient="Voucher recipient",
            code="VOUCHER",
            limit=1
        )
        voucher.save()

        self.set_time(datetime.datetime(2015, 01, 01, tzinfo=UTC))

        cart_1 = CartController.for_user(self.USER_1)
        cart_1.apply_voucher(voucher)
        self.assertIn(voucher, cart_1.cart.vouchers.all())

        # Second user should not be able to apply this voucher (it's exhausted)
        cart_2 = CartController.for_user(self.USER_2)
        with self.assertRaises(ValidationError):
            cart_2.apply_voucher(voucher)

        # After the reservation duration, user 2 should be able to apply voucher
        self.add_timedelta(rego.Voucher.RESERVATION_DURATION * 2)
        cart_2.apply_voucher(voucher)
        cart_2.cart.active = False
        cart_2.cart.save()

        # After the reservation duration, user 1 should not be able to apply
        # voucher, as user 2 has paid for their cart.
        self.add_timedelta(rego.Voucher.RESERVATION_DURATION * 2)
        with self.assertRaises(ValidationError):
            cart_1.apply_voucher(voucher)
