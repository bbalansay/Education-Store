from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.db.models import Avg
from EducationStore.models import List, Cart, Products, Orders, OrderProduct, Favorites, ProductList, Privilege, ProductCategory
from django.db import IntegrityError
import json
import pyodbc
import requests as r
from bs4 import BeautifulSoup as bs
from .forms import SearchForm, EmailForm
import math
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

@csrf_exempt
def list(request):
    """
    All requests require the user to be signed in
    POST: Creates a new list owned by the user
    GET: Returns a template with all of the user's lists
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method  == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return json_error()
        if "name" not in body:
            return missing_param("name")
        description = ""
        if "description" in body:
            description = body["description"]
        list_type = 2
        if "list_type" in body:
            list_type = body["list_type"]
        try:
            new_list = List(name=body["name"],
                            description=description,
                            user_id=request.user,
                            list_type=list_type)
            new_list.save()
        except IntegrityError:
            return bad_request("Failed to create list. Please make sure input is valid.")
        except:
            return server_error("Failed to save list")
        return HttpResponse("New list created", status=status.HTTP_200_OK)
    elif request.method == "GET":
        try:
            data = List.objects.filter(user_id=request.user)
            return render(request, "main/lists.html",
                        {"data": data}, status=200)
        except:
            return server_error("Failed to get lists")
    else:
        return bad_method("Method not allowed")

@csrf_exempt
def specific_list(request, list_id):
    """
    Requires user to be signed in and own the list for all methods except GET.
    Admins can edit any lists.
    IF GET: Returns a template with the products in the list.
    If PATCH: Updates the name and/or description of the list
    If DELETE: Deletes the list if no product is passed. Otherwise deletes product from list
    IF POST: Add product_id to list
    EXTRA CREDIT - Conner - added aggregate to GET request of average price
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    methods = ("GET", "POST", "PATCH", "DELETE")
    if request.method not in methods:
        return bad_method("Method not allowed")
    else:
        if request.method == "GET":
            try:
                list_model = List.objects.get(id=list_id)
                list_dict = list_to_dict(list_model)
                isowner = is_user_list_owner(request.user, list_dict) or is_user_admin(request.user)
                list_model = List.objects.get(id=list_id)
                product_l_model = ProductList.objects.filter(list_id=list_model)
                data = []
                ids = []
                for product_list in product_l_model:
                    product_model = Products.objects.get(id=product_list.product_id.id)
                    ids.append(product_list.product_id.id)
                    data.append({
                        "name": product_model.name,
                        "description": product_model.description,
                        "price": product_model.price,
                        "id": product_model.id
                    })
                avg = Products.objects.filter(pk__in=ids).aggregate(Avg('price'))["price__avg"]
                return render(request, "main/productlist.html",
                            {"data": data, "avg": avg, "list_id": list_id, "isowner": isowner}, status=200)
            except:
                return bad_request("Failed to get list. Make sure the list id is valid.")
        # Get the list and make sure the user has access
        try:
            list_model = List.objects.get(id=list_id)
            list_dict = list_to_dict(list_model)
            if not is_user_list_owner(request.user, list_dict) or is_user_admin(request.user):
                return forbidden()
        except Exception:
            return bad_request("Failed to get list. Make sure the list id is valid.")
        if request.method == "POST":
            # Add a product to the list
            try:
                body = json.loads(request.body.decode('utf-8'))
            except ValueError:
                json_error()
            if not "product_id" in body:
                missing_param("product_id")
            try:
                product = Products.objects.get(id=body["product_id"])
                list_product = ProductList(product_id=product, list_id=list_model)
                list_product.save()
                return HttpResponse("Added to list successfully", status=status.HTTP_200_OK)
            except IntegrityError:
                return bad_request("Failed to add product to list. Please make sure input is valid.")
            except:
                return server_error("Failed to add product to list")
        elif request.method == "PATCH":
            # Update the list name/description
            try:
                body = json.loads(request.body.decode('utf-8'))
            except ValueError:
                json_error()
            if "name" in body:
                list_model.name = body["name"]
            if "description" in body:
                list_model.description = body["description"]
            try:
                list_model.save()
                return JsonResponse(list_to_dict(list_model), safe=False, status=status.HTTP_200_OK)
            except IntegrityError:
                return bad_request("Failed to update list. Please make sure input is valid.")
            except:
                return server_error("Failed to patch list")
        else: # DELETE
            try:
                body = json.loads(request.body.decode('utf-8'))
            except ValueError:
                json_error()
            if not "product_id" in body:
                try:
                    list_model.delete()
                    return HttpResponse("List deleted successfully", status=status.HTTP_200_OK)
                except:
                    return bad_request("Failed to delete list. Please make sure the list exists")
            try:
                product = Products.objects.get(id=body["product_id"])
                list_product = ProductList.objects.filter(product_id=product, list_id=list_model)[0]
                list_product.delete()
                return HttpResponse("Product deleted from list", status=status.HTTP_200_OK)
            except:
                return bad_request("Failed to delete product from list")

@csrf_exempt
def favorites(request):
    """
    Requires user to be signed in and own the list for all methods.
    IF GET: Returns JSON with user's favorite list IDs
    If DELETE: Removes list from favorites
    IF POST: Add list to favorites
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method == "GET":
        ids = []
        try:
            for favorite in Favorites.objects.filter(user_id=request.user):
                ids.append(favorite.list_id.id)
        except:
            return server_error("Failed to get favorites")
        return JsonResponse(ids, safe=False, status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        try:
            body = json.loads(request.body.decode('utf-8'))
        except ValueError:
            json_error()
        if not "list_id" in body:
            missing_param("list_id")
        try:
            list = List.objects.get(id=body["list_id"])
            Favorites.objects.get(user_id=request.user, list_id=list).delete()
        except:
            return bad_request("Failed to delete from favorites")
        return HttpResponse("Successfully removed list from favorites.",
                            status=status.HTTP_200_OK)
    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))
        except ValueError:
            json_error()
        if not "list_id" in body:
            missing_param("list_id")
        try:
            list = List.objects.get(id=body["list_id"])
            new_fav = Favorites(user_id=request.user, list_id=list)
            new_fav.save()
            return HttpResponse("Successfully added list to favorites.",
                                status=status.HTTP_200_OK)
        except IntegrityError:
            return bad_request("Failed to add to list. Please make sure input is valid.")
        except:
            return server_error("Failed to add list to favorites")
    else:
        return bad_method("Method not allowed")

def is_user_list_owner(user, list_dict):
    """Returns true user owns list. False otherwise"""
    return list_dict["user_id"] == user.id

def list_to_dict(list_model):
    """Returns an object with the data from the list_model"""
    return {
        "id": list_model.id,
        "name": list_model.name,
        "description": list_model.description,
        "user_id": list_model.user_id.id,
        "list_type": list_model.list_type
    }

def bad_method(msg):
    """Returns a 405 bad method error with passed in msg"""
    return HttpResponse(msg, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
def edit_cart(request):
    """
    User must be authenticated to edit cart
    GET: Returns HTML with the cart
    POST: Add item to cart
    PATCH: Update quantity of item in cart
    DELETE: Remove item from cart
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method == "GET":
        try:
            data = Products.objects.filter(cart__user_id=request.user)
            return render(request, "main/cart.html",
                        {"data": data}, status=200)
        except:
            return server_error("Failed to get cart")
    elif request.method  == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return json_error()

        if "product_id" not in body:
            return missing_param("product_id")
        if "quantity" not in body:
            return missing_param("quantity")

        pid = body["product_id"]
        qty = body["quantity"]

        try:
            prod = Products.objects.get(id=pid)
            qty = int(qty)
            tot_price = qty * prod.price

            new_item = Cart(user_id=request.user,
                            product_id=prod,
                            quantity=qty,
                            total_cost=tot_price)
            new_item.save()
        except IntegrityError:
            return bad_request("Failed to add to cart. Please make sure input is valid.")
        except Exception:
            return server_error("Failed to add product to cart")
        return HttpResponse("Successfully added new item to cart.", status=status.HTTP_200_OK)
    elif request.method == "PATCH":
        try:
            body = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return json_error()

        if "product_id" not in body:
            return missing_param("product_id")
        if "quantity" not in body:
            return missing_param("quantity")

        pid = body["product_id"]
        qty = body["quantity"]

        try:
            prod = Products.objects.get(id=pid)
            qty = int(qty)
            tot_price = qty * prod.price

            cart_item = Cart.objects.get(user_id=request.user, product_id=prod)

            cart_item.quantity = qty
            cart_item.total_cost = tot_price
            cart_item.save()
        except IntegrityError:
            return bad_request("Failed to update cart. Please make sure input is valid.")
        except Exception:
            return server_error("Failed to update cart")
        return HttpResponse("Cart item successfully updated.", status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        try:
            body = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return json_error()

        if "product_id" not in body:
            return missing_param("product_id")

        pid = body["product_id"]

        try:
            prod = Products.objects.get(id=pid)

            cart_item = Cart.objects.filter(user_id=request.user, product_id=prod)[:1].get()
            cart_item.delete()
        except Exception:
            return server_error("Failed to delete item from cart")
        return HttpResponse("Cart item successfully deleted", status=status.HTTP_200_OK)
    else:
        return HttpResponse("Method not allowed",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
def all_orders(request):
    """
    User must be authenticated to view orders
    GET: Returns a template with a list of all order
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method == "GET":
        orders = []

        try:
            for order in Orders.objects.filter(user=request.user).values():
                order_info = {
                    "id": order.get("id"),
                    "date": order.get("date"),
                    "final_price": order.get("final_price"),
                    "payment_info": order.get("payment_info"),
                    "shipment_status": order.get("shipment_status")
                }

                orders.append(order_info)
            return render(request, 'main/orderhistory.html', {'orders': orders}, status=200)
        except Exception:
            return server_error("Failed to get orders")
    else:
        return HttpResponse("Method not allowed",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
def update_order_status(request, order_id):
    """
    User must be authenticated to edit order information
    User must be an admin to edit
    PATCH: Update the shipping status of an order
    DELETE: Remove order (cancel it)
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.user.Privilege.user_type != "admin":
        return forbidden()

    if request.method == "PATCH":
        body = json.loads(request.body.decode('utf-8'))

        if "shipment_status" not in body:
            return missing_param("shipment_status")

        status = body["shipment_status"]

        try:
            order = Orders.objects.get(id=order_id)

            order.shipment_status = status
            order.save()
        except Exception:
            return bad_request("Failed to save order status. Make sure the ID is valid")
        return HttpResponse("Shipment status of order " + str(order_id) + " has been updated.",
                            status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        try:
            order = Orders.objects.get(id=order_id)
            order.delete()
        except Exception:
            return bad_request("Failed to delete. Make sure the ID is valid.")
        return HttpResponse("Order " + str(order_id) + " has been cancelled.",
                            status=status.HTTP_200_OK)
    else:
        return HttpResponse("Method not allowed",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

def is_user_admin(user):
    return Privilege.objects.filter(user=user, user_type="admin").exists()

@csrf_exempt
def purchase(request):
    """
    User must be authenticated to purchase
    GET: show the items in the cart, the address it will be sent to,
    POST: purchase items in cart (or list if one is passed as list_id)
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method == "GET":
        try:
            desired_items = Cart.objects.filter(user_id=request.user.id)
        except:
            return server_error("Could not get items")
        products = list()
        quantities = list()
        total_price = 0
        for item in desired_items:
            try:
                products.append(Products.objects.get(id=item.product_id))
            except:
                return bad_request("Failed to get product. Make sure ID is valid")
            quantities.append(item.quantity)
            total_price = total_price + item.total_cost
        address = request.user.address
        return render(request, 'main/purchase.html', {'products': products,
                        'address': address, 'total_price': total_price}, status=200)

    elif request.method == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))
        except:
            return(json_error())
        try:
            if "list_id" in body:
                purchased_items = Products.objects.filter(productlist__list_id=body['list_id'])
            else:
                purchased_items = Cart.objects.filter(user_id=request.user)
            total_price = 0
            payment = "************6789"
            if "payment_information" in body:
                payment = body['payment_information']
            newOrder = Orders(user=request.user, final_price=0,
                        payment_info=payment, shipment_status="Not shipped yet")
            newOrder.save()
            for item in purchased_items:
                price = item.total_cost if not "list_id" in body else item.price
                total_price = total_price + price
                order_product = OrderProduct()
                order_product.product_id = item if "list_id" in body else item.product_id
                order_product.order_id = newOrder
            newOrder.final_price = total_price
            newOrder.save()
        except IntegrityError:
            return bad_request("Failed to purchase items. Please make sure input is valid.")
        except Exception:
            return server_error("Failed to make purchase")
        try:
            Cart.objects.filter(user_id=request.user).delete()
        except Exception:
            return server_error("Failed to delete item from cart")
        return HttpResponse("Items Purchased! Thank you for shopping!", status=status.HTTP_200_OK)
    else:
        return HttpResponse("Method not allowed",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
def all_products(request):
    """
    User must be authenticated to POST, not to GET
    GET: Returns a list of product JSON data
    POST: User must be an admin to add a new product
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method == "GET":
        try:
            products = []
            for product in Products.objects.all():
                products.append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "vendor": product.vendor,
                    "image_url": product.image_url
                })
        except Exception:
            return server_error("Failed to get products")
        if len(products) < 5:
            scrape()
        return JsonResponse(products, safe=False)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return not_signed_in()
        if request.user.Privilege.user_type != "admin":
            return forbidden()

        body = json.loads(request.body.decode('utf-8'))

        if "name" not in body:
            return missing_param("name")
        if "product_category" not in body:
            return missing_param("product_category")
        if "price" not in body:
            return missing_param("price")
        if "vendor" not in body:
            return missing_param("vendor")

        try:
            new_name = body["name"]
            new_desc = "No Description"

            if "description" in body:
                new_desc = body["description"]

            prod_cat = ProductCategory.objects.get(category=body["product_category"])
            new_price = body["price"]
            new_vend = body["vendor"]

            new_prod = Products(name=new_name,
                                description=new_desc,
                                product_category=prod_cat,
                                price=new_price,
                                vendor=new_vend)
            new_prod.save()
        except IntegrityError:
            return bad_request("Failed to add product. Please make sure input is valid.")
        except Exception:
            return server_error("Failed to add product")
        return HttpResponse("Successfully added new product.", status=status.HTTP_200_OK)
    else:
        return HttpResponse("Method not allowed",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
def specific_product(request, product_id):
    """
    User must be an admin to edit a product
    GET: Returns product.html rendering of the product
    PATCH: User may choose to update any attribute of the product through JSON
    DELETE: Removes the product from database
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method == "GET":
        try:
            lists = List.objects.filter(user_id=request.user)
            product_model = Products.objects.get(id=product_id)
            return render(request, "main/product.html", {
                "name": product_model.name,
                "description": product_model.description,
                "price": product_model.price,
                "image_url": product_model.image_url,
                "id": product_model.id,
                "lists": lists
            }, status=200)
        except Exception:
            return bad_request("Failed to get product. Make sure the product exists")
    if not request.user.is_authenticated:
        return not_signed_in()
    if is_user_admin(request.user):
        return forbidden()
    if request.method == "PATCH":
        body = json.loads(request.body.decode('utf-8'))
        try:
            prod = Products.objects.get(id=product_id)

            if "name" in body:
                prod.name = body["name"]
            if "description" in body:
                prod.description = body["description"]
            if "product_category" in body:
                prod.product_category = ProductCategory.objects.get(category=body["product_category"])
            if "price" in body:
                prod.price = body["price"]
            if "vendor" in body:
                prod.vendor = body["vendor"]

            prod.save()
        except IntegrityError:
            return bad_request("Failed to edit product. Please make sure input is valid.")
        except Exception:
            return server_error("Failed ot edit product")
        return HttpResponse("Successfully updated product.", status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        try:
            prod = Products.objects.get(id=product_id)
            prod.delete()
        except Exception:
            return bad_request("Failed to delete product. Make sure the product id is valid.")
        return HttpResponse("Successfully deleted product.", status=status.HTTP_200_OK)
    else:
        return HttpResponse("Method not allowed",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
@csrf_exempt
def all_products_html(request):
    """
    GET: Returns all products HTML page.
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method == "GET":
        return render(request, "main/products.html", status=200)
    return HttpResponse("Method not allowed",
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

@csrf_exempt
def home(request):
    """
    GET: Returns HOME html page.
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method == "GET":
        return render(request, "main/home.html", status=200)
    return HttpResponse("Method not allowed",
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

def not_signed_in():
    """Redirect to signin page"""
    return HttpResponseRedirect("/auth/signin")

def server_error(msg):
    """Returns a 500 interal server error with passed in msg"""
    return HttpResponse(msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def bad_request(msg):
    """Returns a 400 bad request error with passed in msg"""
    return HttpResponse(msg, status=status.HTTP_400_BAD_REQUEST)

def json_error():
    """Returns a 400 bad request error due to bad JSON form"""
    return HttpResponse("Failed to load data. Please Make sure to pass valid JSON",
                        status=status.HTTP_400_BAD_REQUEST)

def missing_param(param):
    """Returns a 400 bad request from the parameter missing"""
    return HttpResponse(param + " parameter required",
                        status=status.HTTP_400_BAD_REQUEST)
def forbidden():
    """Returns a 403 forbidden error"""
    return HttpResponse("Forbidden", status=status.HTTP_403_FORBIDDEN)

def scrape():
    """Scrape books and add them to the database"""
    domain = 'http://books.toscrape.com/catalogue/'
    home = domain + 'category/books_1/index.html'
    index_soup = bs(r.get(home).content, 'html.parser')

    books = []
    num_pages = 1

    strongs = index_soup.select('.form-horizontal strong')
    # While not necessary for this current site, if there were less than 50 books
    # and thus only 1 page, this check for strong tags would prevent an error
    if len(strongs) > 1:
        #strongs[0] = number of books, strongs[2] = results per page
        num_pages = math.ceil(int(strongs[0].get_text()) / int(strongs[2].get_text()))

    for page_num in range(1, 2): #UNCOMMENT TO GET ALL BOOKS - TAKES FOREVER num_pages + 1):
        curr_page = domain + 'page-' + str(page_num) + '.html'
        curr_page_soup = bs(r.get(curr_page).content, 'html.parser')
        a_tags = curr_page_soup.select('h3 a')
        for tag in a_tags:
            book_domain = domain + tag['href']
            curr_book_soup = bs(r.get(book_domain).content, 'html.parser')
            genre = curr_book_soup.select('.breadcrumb li > a')[2].get_text().strip()
            name = curr_book_soup.select_one('.product_main h1').get_text()
            price = curr_book_soup.select_one('.price_color').get_text()
            descr_elm = curr_book_soup.select_one('#product_description + p')
            img = "http://books.toscrape.com/" + curr_book_soup.select_one("#product_gallery img")["src"][6:]
            description = None
            if descr_elm is not None:
                description = curr_book_soup.select_one('#product_description + p').get_text()
            books.append((name, description, genre, price, img))

    for book in books:
        new_name = book[0]
        new_desc = book[1]
        new_cat = book[2] + " book"
        new_price = book[3]
        img = book[4]
        new_vend = "Books To Scrape"
        try:
            # Create the category if it doesn't already exist
            category = None
            if not ProductCategory.objects.filter(category=new_cat).exists():
                category = ProductCategory(category=new_cat)
                category.save()
            category = ProductCategory.objects.get(category=new_cat)
            new_prod = Products(name=new_name,
                                description=new_desc[0:254],
                                product_category=category,
                                price=float(new_price[1:]),
                                vendor=new_vend,
                                image_url=img)
            new_prod.save()
        except Exception:
            # Continue adding books even if some fail
            print("There was an error adding a book")

@csrf_exempt
def search(request):
    """Search Google for eBooks, accepts GET and POST"""
    if request.method == "POST":
        post = request.POST
        form = SearchForm(post)
        if not form.is_valid():
            return HttpResponse("Invalid search request", status=400)

        try:
            URL = "https://www.googleapis.com/books/v1/volumes"
            PARAMS = {
                'q': form.cleaned_data['keywords'],
                'filter': 'paid-ebooks'
            }

            response = r.get(url = URL, params = PARAMS)
            data = response.json()['items']

            newForm = SearchForm()
            return render(request, "main/searchresults.html", {'form': newForm, 'data': data}, status=200)
        except:
            newForm = SearchForm()
            return render(request, "main/search.html", {'form': newForm})
    elif request.method == "GET":
        form = SearchForm()
        return render(request, "main/search.html", {'form': form}, status=200)
    else:
        return HttpResponse("Method not allowed on main/search", status=405)

@csrf_exempt
def contactus(request):
    """
    GET: returns the contact us page.
    POST: Sends a message to the creators.
    """
    if request.method == "GET":
        form = EmailForm()
        return render(request, 'main/contactus.html', {'form': form})
    elif request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            subject = sender + "Has contacted you through BookStore"
            recipient_list = ['nhytrek@uw.edu', 'balansay@uw.edu', 'ardmanc@uw.edu']
            email_from = settings.EMAIL_HOST_USER
            send_mail(subject, message, email_from, recipient_list)

            return HttpResponseRedirect("/main/contact")
        else:
            return HttpResponse("Invalid Form",
                            status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return HttpResponse("Method not allowed",
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

def about(request):
    """
    GET: Returns about us page.
    """
    if not request.user.is_authenticated:
        return not_signed_in()

    if request.method == "GET":
        return render(request, "main/about.html", status=200)
    return HttpResponse("Method not allowed",
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
