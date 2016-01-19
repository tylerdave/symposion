from django.core.exceptions import ObjectDoesNotExist

from symposion.registration import models as rego
from cart import CartController

class InvoiceController(object):

    def __init__(self, invoice):
        self.invoice = invoice

    @classmethod
    def for_cart(cls, cart):
        ''' Returns an invoice object for a given cart at its current revision.
        If such an invoice does not exist, the cart is validated, and if valid,
        an invoice is generated.'''

        try:
            invoice = rego.Invoice.objects.get(
                cart=cart, cart_revision=cart.revision)
        except ObjectDoesNotExist:
            cart_controller = CartController(cart)
            cart_controller.validate_cart() # Raises ValidationError on fail.
            invoice = cls._generate(cart)

        return InvoiceController(invoice)

    @classmethod
    def _generate(cls, cart):
        ''' Generates an invoice for the given cart. '''
        invoice = rego.Invoice.objects.create(
            user=cart.user,
            cart=cart,
            cart_revision=cart.revision,
        )

        # TODO: calculate line items.

        return invoice


    def is_valid(self):
        ''' Returns true if the attached invoice is not void and it represents
        a valid cart. '''
        return False

    def void(self):
        ''' Voids the invoice. '''

    def pay(self, reference, amount):
        ''' Pays the invoice by the given amount. If the payment
        equals the total on the invoice, finalise the invoice.
        (NB should be transactional.)
        '''

        pass

    def _finalise(self):
        ''' Marks the invoice as paid, and marks the cart it is attached to as
        inactive. '''
        pass
