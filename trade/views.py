from datetime import datetime

import requests
import pandas as pd
import plotly.graph_objects as go
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Transaction, Order
from users.models import Wallet
from .forms import MarketOrderForm, LimitOrderForm

import pytz
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

SUPPORTED_CURRENCIES = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']  # і т.д.

class CurrentPriceService:
    @staticmethod
    def get_current_price(symbol):
        """Отримати поточну ціну криптовалюти"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url)
            data = response.json()
            return Decimal(data['price'])
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None

@method_decorator(login_required, name='dispatch')
class CurrencyView(View):
    template_name = 'trade/currency_template.html'
    
    def get(self, request, symbol):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        context = self._get_context(wallet, symbol)
        return render(request, self.template_name, context)
    
    def post(self, request, symbol):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self._handle_market_order(request, wallet, symbol)
        
        if 'limit_order' in request.POST:
            return self._handle_limit_order(request, wallet, symbol)
            
        return redirect('currency_view', symbol=symbol)
    
    def _get_context(self, wallet, symbol):
        active_orders = Order.objects.filter(
            wallet=wallet,
            status="OPEN"
        ).order_by('-created_at')
        
        recent_transactions = Transaction.objects.filter(
            wallet=wallet
        ).order_by('-timestamp')[:10]

        # Отримуємо баланс криптовалюти
        crypto_balance = wallet.crypto_balances.get(symbol, 0) if wallet.crypto_balances else 0
        
        return {
            'symbol': symbol,
            'wallet': wallet,
            'market_form': MarketOrderForm(),
            'limit_form': LimitOrderForm(),
            'active_orders': active_orders,
            'recent_transactions': recent_transactions,
            'crypto_balance': crypto_balance,  # Додаємо баланс криптовалюти до контексту
        }
    
    def _handle_market_order(self, request, wallet, symbol):
        try:
            amount = Decimal(request.POST.get('amount'))
            transaction_type = request.POST.get('transaction_type')
            
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")

            # Створюємо транзакцію
            transaction = Transaction(
                user=request.user,
                wallet=wallet,
                transaction_type=transaction_type,
                currency=symbol,
                amount=amount,
                price_usd=CurrentPriceService.get_current_price(symbol)
            )
            
            # Розраховуємо total_usd
            transaction.total_usd = transaction.amount * transaction.price_usd
            
            # Перевіряємо баланс перед збереженням
            if transaction_type == 'BUY':
                if wallet.balance_usd < transaction.total_usd:
                    raise ValueError("Insufficient USD balance")
            else:  # SELL
                crypto_balance = wallet.crypto_balances.get(symbol, 0)
                if Decimal(str(crypto_balance)) < amount:
                    raise ValueError(f"Insufficient {symbol} balance")
            
            # Зберігаємо та виконуємо транзакцію
            transaction.save()
            if transaction.execute_transaction():
                return JsonResponse({
                    'status': 'success',
                    'message': 'Transaction completed successfully'
                })
            else:
                raise ValueError("Transaction execution failed")
            
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f"Unexpected error: {str(e)}"
            })
    
    def _handle_limit_order(self, request, wallet, symbol):
        form = LimitOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.wallet = wallet
            order.currency = symbol
            order.save()
            messages.success(request, 'Limit order created successfully')
        return redirect('currency_view', symbol=symbol)

@method_decorator(login_required, name='dispatch')
class WalletView(TemplateView):
    template_name = 'trade/wallet.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wallets'] = Wallet.objects.filter(user=self.request.user)
        context['transactions'] = Transaction.objects.filter(user=self.request.user).order_by('-timestamp')
        return context

@method_decorator(login_required, name='dispatch')
class CreateOrderView(View):
    def post(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
            order_data = self._get_order_data(request)
            
            if self._validate_order(wallet, order_data):
                Order.objects.create(
                    wallet=wallet,
                    order_type=order_data['order_type'],
                    currency=order_data['currency'],
                    amount=order_data['amount'],
                    limit_price=order_data['price']
                )
                messages.success(request, 'Order created successfully')
            
        except Exception as e:
            messages.error(request, str(e))
            
        return redirect('trade')
    
    def _get_order_data(self, request):
        return {
            'order_type': request.POST.get('order_type'),
            'amount': Decimal(request.POST.get('amount')),
            'price': Decimal(request.POST.get('price')),
            'currency': request.POST.get('currency')
        }
    
    def _validate_order(self, wallet, order_data):
        if order_data['order_type'] == 'SELL':
            if (order_data['currency'] not in wallet.crypto_balances or 
                wallet.crypto_balances[order_data['currency']] < order_data['amount']):
                messages.error(self.request, 'Insufficient balance')
                return False
        return True

@method_decorator(login_required, name='dispatch')
class TradingView(View):
    template_name = 'trade/trading.html'
    
    def get(self, request, symbol):
        context = self._get_context(request, symbol)
        return render(request, self.template_name, context)
    
    def post(self, request, symbol):
        wallet = Wallet.objects.get(user=request.user)
        
        if 'market_order' in request.POST:
            self._handle_market_order(request, wallet, symbol)
        elif 'limit_order' in request.POST:
            self._handle_limit_order(request, wallet)
            
        return redirect('trading', symbol=symbol)
    
    def _get_context(self, request, symbol):
        wallet = Wallet.objects.get(user=request.user)
        return {
            'symbol': symbol,
            'wallet': wallet,
            'market_form': MarketOrderForm(),
            'limit_form': LimitOrderForm(),
            'active_orders': Order.objects.filter(wallet=wallet, status="OPEN").order_by('-created_at'),
            'recent_transactions': Transaction.objects.filter(wallet=wallet).order_by('-timestamp')[:10],
        }
    
    def _handle_market_order(self, request, wallet, symbol):
        try:
            amount = Decimal(request.POST.get('amount'))
            transaction_type = request.POST.get('transaction_type')
            
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")

            # Створюємо транзакцію
            transaction = Transaction(
                user=request.user,
                wallet=wallet,
                transaction_type=transaction_type,
                currency=symbol,
                amount=amount,
                price_usd=CurrentPriceService.get_current_price(symbol)
            )
            
            # Розраховуємо total_usd
            transaction.total_usd = transaction.amount * transaction.price_usd
            
            # Перевіряємо баланс перед збереженням
            if transaction_type == 'BUY':
                if wallet.balance_usd < transaction.total_usd:
                    raise ValueError("Insufficient USD balance")
            else:  # SELL
                crypto_balance = wallet.crypto_balances.get(symbol, 0)
                if Decimal(str(crypto_balance)) < amount:
                    raise ValueError(f"Insufficient {symbol} balance")
            
            # Зберігаємо та виконуємо транзакцію
            transaction.save()
            if transaction.execute_transaction():
                return JsonResponse({
                    'status': 'success',
                    'message': 'Transaction completed successfully'
                })
            else:
                raise ValueError("Transaction execution failed")
            
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f"Unexpected error: {str(e)}"
            })
    
    def _handle_limit_order(self, request, wallet):
        form = LimitOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.wallet = wallet
            order.save()
            messages.success(request, 'Limit order created successfully')

@method_decorator(login_required, name='dispatch')
class CancelOrderView(View):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, wallet__user=request.user)
            if order.cancel_order():
                messages.success(request, 'Order cancelled successfully')
            else:
                messages.error(request, 'Could not cancel order')
        except Order.DoesNotExist:
            messages.error(request, 'Order not found')
        
        return redirect('trading', symbol=order.currency)

class TradingPairsService:
    @staticmethod
    def get_available_pairs():
        """Отримати список доступних торгових пар з Binance"""
        try:
            response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
            data = response.json()
            return [symbol['symbol'] for symbol in data['symbols'] if symbol['status'] == 'TRADING']
        except Exception as e:
            print(f"Error fetching pairs: {e}")
            return SUPPORTED_CURRENCIES


#done