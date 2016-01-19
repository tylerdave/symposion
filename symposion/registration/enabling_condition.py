from symposion.registration import models as rego


class EnablingConditionController(object):

    def __init__(self):
        pass

    @staticmethod
    def for_condition(condition):
        if isinstance(condition, rego.TimeOrStockLimitEnablingCondition):
            return TimeOrStockLimitEnablingConditionController(condition)
        else:
            return EnablingConditionController()

    def user_can_add(self, user, product, quantity):
        return True


class TimeOrStockLimitEnablingConditionController(EnablingConditionController):

    def __init__(self, ceiling):
        self.ceiling = ceiling

    def user_can_add(self, user, product, quantity):
        ''' returns True if adding _quantity_ of _product_ will not vioilate
        this ceiling. '''

        # TODO capture products based on categories
        if product not in self.ceiling.products.all():
            return True

        # TODO: test start_time
        # TODO: test end_time

        # Test limits
        count = 0
        product_items = rego.ProductItem.objects.filter(
            product=self.ceiling.products.all())
        for product_item in product_items:
            if True:
                # TODO: test that cart is paid or reserved
                count += product_item.quantity
        if count + quantity > self.ceiling.limit:
            return False

        # All limits have been met
        return True
