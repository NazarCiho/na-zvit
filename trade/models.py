from django.db import models
from users.models import Wallet
from decimal import Decimal
from django.contrib.auth.models import User


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("BUY", "Buy Cryptocurrency"),
        ("SELL", "Sell Cryptocurrency"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    currency = models.CharField(max_length=10)  
    amount = models.DecimalField(max_digits=15, decimal_places=8) 
    price_usd = models.DecimalField(max_digits=15, decimal_places=2)  
    total_usd = models.DecimalField(max_digits=15, decimal_places=2)  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.total_usd:
            self.total_usd = Decimal(str(self.amount)) * Decimal(str(self.price_usd))
        super().save(*args, **kwargs)

    def execute_transaction(self):
        try:
            if self.transaction_type == "BUY":
                if self.wallet.balance_usd >= self.total_usd:
                    try:
                        self.wallet.subtract_usd(self.total_usd)
                        self.wallet.add_crypto(self.currency, self.amount)
                        self.status = "COMPLETED"
                        self.save()
                        return True
                    except Exception as e:
                        self.wallet.add_usd(self.total_usd)
                        self.status = "FAILED"
                        self.save()
                        raise ValueError(str(e))
                else:
                    self.status = "FAILED"
                    self.save()
                    raise ValueError("Insufficient USD balance")
            else:
                crypto_balance = self.wallet.crypto_balances.get(self.currency, 0)
                if Decimal(str(crypto_balance)) >= self.amount:
                    try:
                        self.wallet.subtract_crypto(self.currency, self.amount)
                        self.wallet.add_usd(self.total_usd)
                        self.status = "COMPLETED"
                        self.save()
                        return True
                    except Exception as e:
                        self.wallet.subtract_usd(self.total_usd)
                        self.wallet.add_crypto(self.currency, self.amount)
                        self.status = "FAILED"
                        self.save()
                        raise ValueError(str(e))
                else:
                    self.status = "FAILED"
                    self.save()
                    raise ValueError(f"Insufficient {self.currency} balance")
                
        except Exception as e:
            self.status = "FAILED"
            self.save()
            raise ValueError(str(e))

    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.currency} at {self.price_usd} USD"


class Order(models.Model):
    ORDER_TYPES = [
        ("LIMIT_BUY", "Limit Buy"),
        ("LIMIT_SELL", "Limit Sell"),
    ]
    
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("FILLED", "Filled"),
        ("CANCELLED", "Cancelled"),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="orders")
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES)
    currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=15, decimal_places=8)
    limit_price = models.DecimalField(max_digits=15, decimal_places=2)
    filled_amount = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def cancel_order(self):
        if self.status == "OPEN":
            self.status = "CANCELLED"
            self.save()
            return True
        return False
