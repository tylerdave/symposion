from django.utils import timezone

from symposion.registration import models as rego


class ConditionController(object):
    ''' Base class for testing conditions that activate EnablingCondition
    or Discount objects. '''

    def __init__(self):
        pass

    @staticmethod
    def for_condition(condition):
        CONTROLLERS = {
            rego.CategoryEnablingCondition : CategoryConditionController,
            rego.IncludedProductDiscount : ProductConditionController,
            rego.ProductEnablingCondition : ProductConditionController,
            rego.TimeOrStockLimitEnablingCondition :
                TimeOrStockLimitConditionController,
            rego.VoucherEnablingCondition : VoucherConditionController,
        }

        try:
            return CONTROLLERS[type(condition)](condition)
        except KeyError:
            return ConditionController()


    def is_met(self, user, quantity):
        return True


class CategoryConditionController(ConditionController):

    def __init__(self, condition):
        self.condition = condition

    def is_met(self, user, quantity):
        ''' returns True if the user has a product from a category that invokes
        this condition in one of their carts '''

        carts = rego.Cart.objects.filter(user=user)
        enabling_products = rego.Product.objects.filter(
            category=self.condition.enabling_category)
        products = rego.ProductItem.objects.filter(cart=carts,
            product=enabling_products)
        return len(products) > 0


class ProductConditionController(ConditionController):
    ''' Condition tests for ProductEnablingCondition and
    IncludedProductDiscount. '''

    def __init__(self, condition):
        self.condition = condition

    def is_met(self, user, quantity):
        ''' returns True if the user has a product that invokes this
        condition in one of their carts '''

        carts = rego.Cart.objects.filter(user=user)
        products = rego.ProductItem.objects.filter(cart=carts,
            product=self.condition.enabling_products.all())
        return len(products) > 0


class TimeOrStockLimitConditionController(ConditionController):
    ''' Condition tests for TimeOrStockLimit EnablingCondition and
    Discount.'''

    def __init__(self, ceiling):
        self.ceiling = ceiling


    def is_met(self, user, quantity):
        ''' returns True if adding _quantity_ of _product_ will not vioilate
        this ceiling. '''

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


class VoucherConditionController(ConditionController):
    ''' Condition test for VoucherEnablingCondition and VoucherDiscount.'''

    def __init__(self, condition):
        self.condition = condition

    def is_met(self, user, quantity):
        ''' returns True if the user has the given voucher attached. '''
        carts = rego.Cart.objects.filter(user=user,
            vouchers=self.condition.voucher)
        return len(carts) > 0
