from django.contrib import admin

# Register your models here.
from .models import Transaction, Order

admin.site.register(Transaction)
admin.site.register(Order)