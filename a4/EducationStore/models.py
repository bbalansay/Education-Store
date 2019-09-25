from django.db import models
from django.contrib.auth.models import User

quantity = [
    ("0", "0"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("10", "10"),
]

list_types = [
    ("tb", "textbooks"),
    ("ss", "school supplies"),
    ("mixed", "mixed")
]

user_types = [
    ("teacher", "teacher"),
    ("student", "student"),
    ("seller", "seller"),
    ("admin", "admin")
]

# Create your models here.
class Privilege(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(choices=user_types, blank=False, default="student", max_length=25)

    def save(self, *args, **kwargs):
        for tup in user_types:
            if self.user_type in tup:
                super().save(*args, **kwargs)

        return "Error: That type of user does not exist."

class ProductCategory(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(blank=False, default="All", max_length=100)

class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=False, default="Blank", max_length=255)
    description = models.CharField(blank=True, default="No Description", max_length=255)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=9.99)
    vendor = models.CharField(blank=False, default="ACME", max_length=255)
    image_url = models.CharField(blank=False, default="https://acacia-wood.com/themes/jtherczeg-multi//assets/images/acacia/empty-img.png", max_length=512)

    def save(self, *args, **kwargs):
        if self.price < 0:
            return "Price cannot be below 0"
        elif self.name == self.description:
            return "Name must be different from description"
        else:
            super().save(*args, **kwargs)

class Cart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(choices=quantity, blank=False, default=1)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=0)

class List(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=False, default="New List", max_length=255)
    description = models.CharField(blank=True, max_length=255)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    list_type = models.CharField(choices=list_types, blank=False, default="mixed", max_length=25)

    def save(self, *args, **kwargs):
        if self.name == self.description:
            return "Name and description must be different"
        else:
            super().save(*args, **kwargs)

class ProductList(models.Model):
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    list_id = models.ForeignKey(List, on_delete=models.CASCADE)

class Favorites(models.Model):
    list_id = models.ForeignKey(List, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

class Orders(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    final_price = models.DecimalField(max_digits=8, decimal_places=2, default=99999.99, blank=False)
    payment_info = models.CharField(max_length=250, default="N/A", blank=False)
    shipment_status = models.CharField(max_length=250, default="N/A", blank=False)

    def save(self, *args, **kwargs):
        if self.final_price < 0:
            return "Price cannot be below 0"
        else:
            super().save(*args, **kwargs)

class OrderProduct(models.Model):
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
