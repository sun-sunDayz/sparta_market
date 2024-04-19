from django.db import models
from accounts.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver


# Create your models here.
class Products(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to="product_images/")
    stock = models.IntegerField(default=0)
    sale_price = models.IntegerField(default=0)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hits = models.IntegerField(default=0)
    likey = models.ManyToManyField(User, related_name="likey", blank=True)
    score = models.FloatField(default=0)
    display_price = models.IntegerField(default=0)
    wishuser = models.ManyToManyField(User, related_name="wishprod", blank=True)


    def __str__(self):
        return f"{self.title} - {self.seller.username}"
    
    def getpic(self):
        if self.image:
            return self.image.url
        return "/static/images/noprod.png"
    
    def getstock(self):
        if self.stock == 0:
            return "품절"
        elif self.stock < 10:
            return f"품절 임박 ({self.stock} left)"
        return "재고 있음"
    
    def is_avail(self):
        if self.stock > 0:
            return True
        return False
    
    class Meta:
        pass




class HashTag(models.Model):
    name = models.CharField(max_length=50)
    products = models.ManyToManyField(Products, related_name="hashtags")

    def __str__(self):
        return self.name

    class Meta:
        pass

@receiver(pre_delete, sender=Products)
def remove_unused_hashtags(sender, instance, **kwargs):
    hashtags = instance.hashtags.all()
    for hashtag in hashtags:
        if hashtag.products.count() <= 1:
            hashtag.delete()


class BuyList(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="buylist")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buylist")
    quantity = models.IntegerField()
    priced = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.buyer.username} - {self.quantity}"

    class Meta:
        pass


class PointHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pointhistory")
    change_amount = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.change_amount} - {self.reason}"

        