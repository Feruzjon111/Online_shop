from django.contrib.auth.models import User
from django.db import models
from app_users.models import Customer, UserModel


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    image = models.ImageField(
        upload_to='images/', default='images/default.jpg')
    old_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    new_price = models.DecimalField(decimal_places=2, max_digits=10)
    is_sale = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.value for r in ratings) / ratings.count(), 1)
        return 0

    def __str__(self):
        return self.name

class Rating(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    value = models.IntegerField(choices=RATING_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.user} - {self.value}"


class Comment(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.owner.get_full_name()} - {self.body[:100]}"


class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            ('product_id', 'user_id'),
        )

    @property
    def total_price(self):
        return self.quantity * self.product.new_price

    def __str__(self):
        return f"{self.user} - {self.product}"