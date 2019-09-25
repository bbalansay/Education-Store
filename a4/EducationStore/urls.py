from django.urls import path
from . import views

app_name = 'auth'
urlpatterns = [
        path('list', views.list, name='list'),
        path('list/<int:list_id>', views.specific_list, name='edit list'),
        path('favorites', views.favorites, name='favorites'),
        path('purchase', views.purchase, name='purchase'),
        path('products/<int:product_id>', views.specific_product, name='specific product'),
        path('products/', views.all_products_html, name='all products'),
        path('products/api', views.all_products, name='products api'),
        path('cart', views.edit_cart, name="edit cart"),
        path('search', views.search, name="search"),
        path('', views.home, name='home'),
        path('purchase/history', views.all_orders, name='order history'),
        path('contact', views.contactus, name="contactus"),
        path('about', views.about, name="about")
]
