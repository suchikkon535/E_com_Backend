from django.db import models
from django.conf import settings  # <-- needed for user
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User

def generate_unique_id():
    return get_random_string(length=8).upper()


class Item(models.Model):
    id = models.CharField(primary_key=True, max_length=10, editable=False, default=generate_unique_id)
    title = models.CharField(max_length=200)
    startPrice = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    endPrice = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.CharField(max_length=100, default="")
    description = models.TextField()

    def __str__(self):
        return self.title


class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="item_images/")

    def __str__(self):
        return f"Image for {self.item.title}"

