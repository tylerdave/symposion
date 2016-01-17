# Workflow

## Definitions
- User has one 'active Cart' at a time. The Cart remains active until a paid Invoice is attached to it.
- A 'paid Cart' is a Cart with a paid Invoice attached to it, where the Invoice has not been voided.
- An Item is 'reserved' if:
  - it belongs to an 
  - it belongs to a paid Cart
- An unpaid Cart is 'reserved' if 
 - CURRENT_TIME - "Time last updated" <= max(reservation duration of Products in Cart),
 - A Voucher was added and CURRENT_TIME - "Time last updated" < VOUCHER_RESERVATION_TIME (15 minutes?)
- A Cart can have any number of Items added to it, subject to limits.


## Entering Vouchers
- Vouchers are attached to Carts
- A user can enter codes for as many different Vouchers as they like.
- A Voucher is added to the Cart if the number of paid or reserved Carts containing the Voucher is less than the "total available" for the voucher.


## Displaying Products:

- If there is at least one EnablingCondition attached to the Product, display it only if at least one EnablingCondition is met
- If there are zero EnablingConditions attached to the Product, display it
- If the user has exceeded the "Limit per user" for the Product in their active and paid Carts, display it as "unavailable".
- If the Product belongs to an exhausted Ceiling, display it as "unavailable".

- If the Product is displayed and available, its price is the price for the Product, minus the greatest Discount available to this Cart and Product

- The product is displayed per the rendering characteristics of the Category it belongs to


## Displaying Categories

- If the Category contains only "unavailable" Products, mark it as "unavailable"
- If the Category contains no displayed Products, do not display the Category
- If the Category contains at least one EnablingCondition, display it only if at least one EnablingCondition is met
- If the Category contains no EnablingConditions, display it


## Exhausting Ceilings
- A ceiling is exhausted if:
 - Its start date has not yet been reached
 - Its end date has been exceeded
 - The sum of each total item 


## Adding Items to the Cart

- Only Products that are displayed and not marked as "unavailable" may be added to a cart (i.e. revalidate display properties)
- If a different price applies to a Product when it is added to a cart, add at the new price, and display an alert to the user






# Models

## Transaction Models

- Cart:
 - (Item = Product Instances)
 - (Voucher Instances)
 - Time last updated

- Invoice:
 - Cart
 - (Invoice Details)
 - Paid?
 - Voided?


## Inventory Model

- Product:
 - Name
 - Category
 - Price
 - Limit per user
 - Reservation duration
 - Display order
 - {Ceilings}
 - {EnablingConditions}


- Voucher
 - Code
 - Total available


- Category?
 - Name
 - Display Order
 - Rendering Style
 - {EnablingConditions}


- Ceiling
 - Start date
 - End date
 - Total available


## Product Modifiers

- Discount:
 - {(Product, Amount, Percentage)}

 - Discount Types:
    - LimitedAvailabilityDiscount:
     - Start date
     - End date
     - Total available

    - VoucherDiscount:
     - Voucher

    - InclusionDiscount:
     - {Parent Product}



- EnablingCondition:

 - EnablingCondition Types:
   - ProductEnablingCondition:
    - {Products that enable}

   - VoucherEnablingCondition:
     - Voucher
   
   - RoleEnablingCondition:
     - Role
