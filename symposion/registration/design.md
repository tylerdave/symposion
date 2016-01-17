# Workflow

## Definitions
- User has one 'active Cart' at a time. The Cart remains active until a paid Invoice is attached to it.
- A 'paid Cart' is a Cart with a paid Invoice attached to it, where the Invoice has not been voided.
- An unpaid Cart is 'reserved' if 
 - CURRENT_TIME - "Time last updated" <= max(reservation duration of Products in Cart),
 - A Voucher was added and CURRENT_TIME - "Time last updated" < VOUCHER_RESERVATION_TIME (15 minutes?)
- An Item is 'reserved' if:
  - it belongs to a reserved Cart
  - it belongs to a paid Cart
- A Cart can have any number of Items added to it, subject to limits.


## Entering Vouchers
- Vouchers are attached to Carts
- A user can enter codes for as many different Vouchers as they like.
- A Voucher is added to the Cart if the number of paid or reserved Carts containing the Voucher is less than the "total available" for the voucher.


## Are products available? 

- Availability is determined by the number of items we want to add to the cart: items_to_add

- If items_to_add + count(Product in their active and paid Carts) > "Limit per user" for the Product, the Product is "unavailable".
- If the Product belongs to an exhausted Ceiling, the Product is "unavailable".
- Otherwise, the product is available


## Displaying Products:

- If there is at least one EnablingCondition attached to the Product, display it only if at least one EnablingCondition is met
- If there are zero EnablingConditions attached to the Product, display it
- If the product is not available for items_to_add=0, mark it as "unavailable"

- If the Product is displayed and available, its price is the price for the Product, minus the greatest Discount available to this Cart and Product

- The product is displayed per the rendering characteristics of the Category it belongs to


## Displaying Categories

- If the Category contains only "unavailable" Products, mark it as "unavailable"
- If the Category contains no displayed Products, do not display the Category
- If the Category contains at least one EnablingCondition, display it only if at least one EnablingCondition is met
- If the Category contains no EnablingConditions, display it


## Exhausting Ceilings

- Exhaustion is determined by the number of items we want to add to the cart: items_to_add

- A ceiling is exhausted if:
 - Its start date has not yet been reached
 - Its end date has been exceeded
 - items_to_add + sum(paid and reserved Items for each Product in the ceiling) > Total available


## Adding Items to the Cart

- Products that are not displayed may not be added to a Cart
- The requested number of items must be available for those items to be added to a Cart
- If a different price applies to a Product when it is added to a cart, add at the new price, and display an alert to the user
- Adding an item resets the "Time last updated" for the cart


## Generating an invoice

- User can ask to 'check out' the active Cart. Doing so generates an Invoice.
- Checking out the active Cart resets the "Time last updated" for the cart. 
- The invoice represents the current state of the cart.
- If a new item is added to the cart, the invoice is voided.


## Paying an invoice

- A payment can only be attached to an invoice if all of the items in it are available at the time payment is processed

### One-Shot
- Update the "Time last updated" for the cart based on the expected time it takes for a payment to complete
- Verify that all items are available, and if so:
- Proceed to make payment
- Apply payment record from amount received


### Authorization-based approach:
- Capture an authorization on the card
- Verify that all items are available, and if so:
- Apply payment record
- Take payment



# Models

## Transaction Models

- Cart:
 - User
 - (Item = Product Instances)
 - (Voucher Instances)
 - Time last updated

- Invoice:
 - Invoice number
 - Cart
 - (Invoice Details)
 - {Payments}
 - Voided?

- Payment
 - Time
 - Amount
 - Reference


## Inventory Model

- Product:
 - Name
 - Category
 - Price
 - Limit per user
 - Reservation duration
 - Display order
 - {Ceilings}


- Voucher
 - Description
 - Code
 - Total available


- Category?
 - Name
 - Display Order
 - Rendering Style


- Ceiling
 - Name
 - Start date
 - End date
 - Total available


## Product Modifiers

- Discount:
 - Description
 - {DiscountForProduct}

 - Discount Types:
    - LimitedAvailabilityDiscount:
     * A discount that is available for a limited amount of time, e.g. Early Bird sales *
     - Start date
     - End date
     - Total available

    - VoucherDiscount:
     * A discount that is available to a specific voucher *
     - Voucher

    - RoleDiscount
     * A discount that is available to a specific role *
     - Role

    - IncludedProductDiscount:
     * A discount that is available because another product has been purchased *
     - {Parent Product}

- DiscountForProduct
 - Product
 - Amount
 - Percentage


- EnablingCondition:
 - {Products}
 - {Categories}

 - EnablingCondition Types:
   - ProductEnablingCondition:
    * Enabling because the user has purchased a specific product *
    - {Products that enable}

   - CategoryEnablingCondition:
    * Enabling because the user has purchased a product in a specific category *
    - {Categories that enable}

   - VoucherEnablingCondition:
    * Enabling because the user has entered a voucher code *
     - Voucher
   
   - RoleEnablingCondition:
     * Enabling because the user has a specific role *
     - Role
