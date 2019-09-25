from django.contrib import admin
from EducationStore.models import List, Cart, Products, Orders, OrderProduct, Favorites, ProductList
# Register your models here.
admin.site.register(List)
admin.site.register(Cart)
admin.site.register(Products)
admin.site.register(Orders)
admin.site.register(OrderProduct)
admin.site.register(Favorites)
admin.site.register(ProductList)
