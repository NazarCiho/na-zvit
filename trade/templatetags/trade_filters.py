from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def calculate_total_balance(crypto_balances, prices, usdt_balance):
    total = float(usdt_balance)
    if crypto_balances:
        for currency, amount in crypto_balances.items():
            try:
                price = float(prices.get(currency, 0))
                value = float(amount) * price
                total += value
            except (ValueError, TypeError):
                continue
    return round(total, 2)

@register.simple_tag
def calculate_total_btc(crypto_balances, prices, usdt_balance):
    total_usd = float(usdt_balance)
    if crypto_balances:
        for currency, amount in crypto_balances.items():
            try:
                price = float(prices.get(currency, 0))
                value = float(amount) * price
                total_usd += value
            except (ValueError, TypeError):
                continue
    
    try:
        btc_price = float(prices.get('BTC', 0))
        if btc_price > 0:
            return round(total_usd / btc_price, 8)
    except (ValueError, TypeError):
        pass
    return 0