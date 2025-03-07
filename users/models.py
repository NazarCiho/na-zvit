import random, pyotp
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from users.utils import upload_to_imgbb
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    is_2fa_authenticated = models.BooleanField(default=False)
    profile_picture = models.URLField(blank=True, default='https://i.ibb.co/xqNGxfX/default.png')
    custom_id = models.CharField(max_length=8, unique=True, blank=True, null=True)  # нове поле для ID
    phone_number = PhoneNumberField(blank=True, null=True)  # Додаємо поле для номера телефонуpip install django-phonenumber-field
    country = models.CharField(max_length=120, blank=True, null=True)  # Поле для країни


    def generate_totp_secret(self):
        self.totp_secret = pyotp.random_base32()
        self.save()

    def provisioning_uri(self):
        totp = pyotp.TOTP(self.totp_secret)
        return totp.provisioning_uri(self.user.username, issuer_name="CryptoExchange")

    def generate_custom_id(self):
        """Метод для генерування випадкового 8-значного ID"""
        self.custom_id = str(random.randint(10000000, 99999999))  # генеруємо випадкове число з восьми цифр
        self.save()

class EmailConfirmation(models.Model):
    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(max_length=6)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

#==========================WALLET=============================#



class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance_usd = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    crypto_balances = models.JSONField(default=dict, null=True)

    def add_usd(self, amount):
        if amount <= 0:
            raise ValueError("Сума поповнення має бути більшою за 0")
        self.balance_usd += Decimal(amount)
        self.save()

    def subtract_usd(self, amount):
        if amount <= 0:
            raise ValueError("Сума зняття має бути більшою за 0")
        if self.balance_usd < Decimal(amount):
            raise ValueError("Недостатньо коштів на балансі")
        self.balance_usd -= Decimal(amount)
        self.save()

    def add_crypto(self, currency, amount):
        if amount <= 0:
            raise ValueError("Сума поповнення має бути більшою за 0")
        if self.crypto_balances is None:
            self.crypto_balances = {}
        balances = self.crypto_balances
        current_amount = Decimal(str(balances.get(currency, 0)))
        balances[currency] = float(current_amount + Decimal(str(amount)))
        self.crypto_balances = balances
        self.save()

    def subtract_crypto(self, currency, amount):
        if amount <= 0:
            raise ValueError("Сума зняття має бути більшою за 0")
        if self.crypto_balances is None:
            raise ValueError(f"Недостатньо {currency} на балансі")
        balances = self.crypto_balances
        if currency not in balances:
            raise ValueError(f"Недостатньо {currency} на балансі")
        current_amount = Decimal(str(balances[currency]))
        if current_amount < Decimal(str(amount)):
            raise ValueError(f"Недостатньо {currency} на балансі")
        balances[currency] = float(current_amount - Decimal(str(amount)))
        if balances[currency] == 0:
            del balances[currency]
        self.crypto_balances = balances
        self.save()

    def __str__(self):
        return f"{self.user.username}'s Wallet (USD: {self.balance_usd})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
        profile.generate_custom_id()  # Генеруємо custom_id після створення профілю
        profile.save()


@receiver(post_save, sender=UserProfile)
def upload_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture and not instance.profile_picture.startswith("http"):
        api_key = "620b20cce0b56095360ae5f1c0d6d289"  # замініть на ваш API ключ
        try:
            image_url = upload_to_imgbb(instance.profile_picture.path, api_key)
            instance.profile_picture = image_url  # Оновлюємо поле URL
            instance.save()
        except Exception as e:
            print(f"Failed to upload image: {e}")


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(user=instance)
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if created:
            profile.generate_custom_id()

@receiver(post_save, sender=User)
def save_user_wallet(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'wallet'):
            instance.wallet.save()
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except Exception as e:
        print(f"Error saving wallet or profile: {e}")


