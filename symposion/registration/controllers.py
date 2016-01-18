from symposion.registration import models as rego

class ProductController(object):

    def __init__(self, product):
        self.product = product

    def user_can_add_within_limit(self, user, quantity):
        ''' Return true if the user is able to add _quantity_ to their count of
        this Product without exceeding _limit_per_user_.'''

        carts = rego.Cart.objects.filter(user=user)
        items = rego.ProductItem.objects.filter(product=self.product, cart=carts)

        count = 0
        for item in items:
            count += item.quantity

        if quantity + count > self.product.limit_per_user:
            return False
        else:
            return True

    def can_add_within_ceilings(self, quantity):
        ''' Returns true is the user is able to add _quantity_ to their count
        of this Product without exceeding the ceilings the product is attached
        to. '''

        ceilings = rego.TimeOrStockLimitEnablingCondition.objects.filter(products=self.product)
        for ceiling in ceilings:
            ceil = CeilingController(ceiling)
            if not ceil.quantity_within_ceiling(self.product, quantity):
                return False
        else:
            return True


class CeilingController(object):

    def __init__(self, ceiling):
        self.ceiling = ceiling

    def quantity_within_ceiling(self, product, quantity):
        ''' returns True if adding _quantity_ of _product_ will not vioilate
        this ceiling. '''

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
