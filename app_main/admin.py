from django.contrib import admin

from .models import Product, Comment, Cart, Rating


admin.site.register(Product)
admin.site.register(Comment)
admin.site.register(Cart)
admin.site.register(Rating)
