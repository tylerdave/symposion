from django.utils import timezone

from symposion.registration import models as rego


class EnablingConditionController(object):

    def __init__(self):
        pass


    @staticmethod
    def for_condition(condition):
        if isinstance(condition, rego.ProductEnablingCondition):
            return ProductEnablingConditionController(condition)
        if isinstance(condition, rego.TimeOrStockLimitEnablingCondition):
            return TimeOrStockLimitEnablingConditionController(condition)
        elif isinstance(condition, rego.VoucherEnablingCondition):
            return VoucherEnablingConditionController(condition)
        else:
            return EnablingConditionController()


    def user_can_add(self, user, product, quantity):
        return True


class ProductEnablingConditionController(EnablingConditionController):

    def __init__(self, condition):
        self.condition = condition

    def user_can_add(self, user, product, quantity):
        ''' returns True if the user has a product that invokes this
        condition in one of their carts '''

        carts = rego.Cart.objects.filter(user=user)
        products = rego.ProductItem.objects.filter(cart=carts,
            product=self.condition.enabling_products.all())
        return len(products) > 0


class TimeOrStockLimitEnablingConditionController(EnablingConditionController):

    def __init__(self, ceiling):
        self.ceiling = ceiling


    def user_can_add(self, user, product, quantity):
        ''' returns True if adding _quantity_ of _product_ will not vioilate
        this ceiling. '''

        # TODO capture products based on categories
        if product not in self.ceiling.products.all():
            return True

        # Test date range
        if not self.test_date_range():
            return False

        # Test limits
        if not self.test_limits(quantity):
            return False

        # All limits have been met
        return True


    def test_date_range(self):
        now = timezone.now()

        if self.ceiling.start_time is not None:
            if now < self.ceiling.start_time:
                return False

        if self.ceiling.end_time is not None:
            if now > self.ceiling.end_time:
                return False

        return True


    def test_limits(self, quantity):
        if self.ceiling.limit is None:
            return True

        count = 0
        product_items = rego.ProductItem.objects.filter(
            product=self.ceiling.products.all())
        reserved_carts = rego.Cart.reserved_carts()
        for product_item in product_items:
            if product_item.cart in reserved_carts:
                count += product_item.quantity

        if count + quantity > self.ceiling.limit:
            return False

        return True


class VoucherEnablingConditionController(EnablingConditionController):

    def __init__(self, condition):
        self.condition = condition

    def user_can_add(self, user, product, quantity):
        ''' returns True if the user has the given voucher attached. '''
        carts = rego.Cart.objects.filter(user=user,
            vouchers=self.condition.voucher)
        return len(carts) > 0
