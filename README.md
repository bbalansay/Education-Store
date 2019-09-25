# education-a4
Conner Ardman, Bradley Balansay, Nick Hytrek

## Database ERD
![erd](https://github.com/info441-sp19/education-a4/blob/master/a4%20schema-2019-05-14_17_12.png)

## Endpoints

`main/home`:
- User must be authenticated to access this endpoint
- If a user is not authenticated they are redirected to the sign in page
- GET: Returns a template with the home screen
  - Returns a 200 with an okay or a 405 if any other method is used


`main/list`:
- User must be signed in to access the endpoint
- If a user is not signed in they are redirected to the sign in page
- GET: Returns a template with all of the user's lists
- POST: Creates a new list owned by the user with passed in name/description
  - Returns 200 with an OK message on success or a 500 on server errors
  Example input:
  ```
  {
    "name": "listname",
    "description": "list description"
  }
  ```

`main/list/<int:list_id>`:
- User must be signed in to access the endpoint
- If a user is not signed in they are redirected to the sign in page
- GET: Returns a template with the products in the list and an aggregate average price
- PATCH: Updates the name and/or description of the list.
  - Returns 200 with JSON of the new list on success. 500 server error on failure.
  - Input format the same as main/list POST
- DELETE: Deletes the list if no product is passed. Otherwise deletes product from list.
  - Returns 200 with an OK message on success or a 500 on server errors
  Example input to delete a product:
  ```
  {
    "product_id": 1
  }
  ```
- POST: Add passed in product_id to list
  - Returns 400 if product_id is missing. 200 on success and 500 on server error.
  Example input:
  ```
  {
    "product_id": 1
  }
  ```

`main/favorites`
- User must be signed in to access the endpoint
- If a user is not signed in they are redirected to the sign in page
- GET: Returns JSON with user's favorite list IDs. 500 error on failure.
- DELETE: Removes list with list_id from favorites
  - Returns 400 if list_id is missing. 200 on success and 500 on server error.
  Example Input:
  ```
  {
    "list_id": 1
  }
  ```
- POST: Add list to favorites
  - Returns 400 if list_id is missing. 200 on success and 500 on server error.
  - Input format the same as delete above.

`main/products`:
- User must be signed in to access the endpoint
- If a user is not signed in they are redirected to the sign in page
- GET: Runs javascript that displays products in the database
  - Returns 200 with an OK message or 405 if any other method request is used

`main/products/<int:product_id>`:
- User must be authenticated to edit the information of a product
- If a user is not signed in they are redirected to the sign in page
- User must be an admin to edit information of a product
- A 403 error is thrown if the user trys to edit information and is not an admin
- A 405 error is thrown if a method that is not PATCH or DELETE is attempted
- A 500 error is thrown if the given JSON data contains bad values
- PATCH:
  - User may choose to update any attribute of the product besides id
  - User specifies changes through JSON
  - Returns 200 upon success, 500 otherwise
- Sample JSON input for PATCH
```
{
  "name": "pencil",
  "description": "N/A",
  "product_category": "school supplies",
  "price": 0.50,
  "vendor": "ACME"
}
```
- DELETE
  - User attempts to delete product, returning 200 if successful and 500 otherwise


`main/purchase`:
- User must be authenticated to make a purchase
- If a user is not signed in they are redirected to the sign in page
- User must be the same user that owns the cart to make the purchase
- A 403 error is thrown if a method t
- A 405 error is thrown if a method that is not GET or POST is attempted
- A 500 error is thrown if the given JSON data contains bad values
- GET:
  - Shows all the items that were in the cart when the purchase was initiated in HTML
  - Shows the address the user has on file that the purchase will be sent to and the total cost of the purchase in HTML
  - returns a 200 when called
- POST:
  - Removes all items in the cart table relating to that user
  - Creates a new Order object for the specific order and adds all of the products relating to the order to the OrderProduct Associative
    table
  - If user passes list_id, purchases items in list instead of cart
  - If the user submits new payment information, the payment information is updated, otherwise the information associated to the user will
    be used
  - returns a 200 upon success, 500 otherwise
  - input example:
    {payment-information: "1234-5678-9123-4567"}
- Sample POST input
```
{
  "payment_information": "1234-5678-9123-4567"
}
```

`main/Search`:
- Users do not need to be signed in to search
- GET:
  - Shows a form allowing for search input
- POST:
  - Displays ebbok information that can be purchased online through the Google Books API
- A 405 error is thrown if a method that is not GET or POST is attempted
- Sample output
```
{
  "cover": "url",
  "title": "alfred's intermediate snare drum solos",
  "authors": ["Dave Black", "Sandy Feldstein", "Jay Wanamaker"],
  "Description": " Alfred's Intermediate Snare Drum Solos feature all of the solo material contained in Alfred's Drum Method",
  "price": 5.38
}
```

`main/cart`:
- User must be authenticated to have a cart
- If a user is not signed in they are redirected to the sign in page
- User must be the same user that owns the cart to make the edits
- A 405 error is raised if any other request method is sent
- GET:
  - Displays items that have been added to the users cart
  - 200 if successful, 500 if the cart doesn't exist
- POST:
  - Takes a product id and a quantity and adds to the cart
  - 200 if successful, 400 if bad input, 500 if product doesn't exist in the databse
  - Sample input
  ```
  {
    "product_id": 1,
    "quantity": 1
  }
  ```
- PATCH:
  - Takes a product id and quantity
  - Condition: The product id must already be in the cart
  - Changes the quanity of an item already in the cart
  - Sends a 200 if successful, 400 if bad input, 500 if product doesn't exist in the database
  - Sample input
  ```
  {
    "product_id": 1,
    "quantity": 3
  }
  ```
- DELETE:
  - Takes a product_id and removes that product from the cart if it is in the cart
  - Sends a 200 if successful, a missing parameter error if the parameter is missing, and a 500 if the item is not in the cart
  - Sample input
  ```
  {
    "product_id": 1
  }
  ```

`main/products/api`:
- User must be authenticated to POST not to GET
- A 405 error is raised if any method other than POST or GET is sent
- GET:
  - Returns all products in JSON
  - If there are less than five products, it will scrape to add more
  - If the products are not in the database it returns a 500 error
- POST:
  - You must be autheticated as an admin user
  - Allows you to add a product to the database
  - 200 if successful, 500 if it fails to add to the database

`main/purchase/history`:
- User must be authenticated to view this endpoint
- a 405 error is raised if any method other than GET is used
- GET:
  - Returns a template with all of the users' previous orders
  - 200 if successful

`main/about`:
- User must be authenticated to view this endpoint
- a 405 error is raised if any method other than GET is used
- GET:
  - Returns a page with information about the store creators
  - 200 if successful

`main/contact`:
- User must be authenticated to view this endpoint
- a 405 error is raised if any method other than GET or POST is used
- GET:
  - Returns a page with contact information
  - 200 if successful
- POST:
  - Sends an email to the creators of the website using a form
  - 200 if successful, 406 if the form in not filled out correctly
  - Sample input
  ```
  {
    "sender": "test@test.com"
    "message": "Hello, I love you"
  }
  ```
