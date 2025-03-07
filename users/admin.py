from django.contrib import admin
from .models import UserProfile, Wallet, EmailConfirmation

admin.site.register(UserProfile)
admin.site.register(EmailConfirmation)
admin.site.register(Wallet)



