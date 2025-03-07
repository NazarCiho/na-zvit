from django.urls import path
from . import views

urlpatterns = [
    path('spot/<str:symbol>/', views.CurrencyView.as_view(), name='currency_view'),
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('create-order/', views.CreateOrderView.as_view(), name='create_order'),
    path('trading/<str:symbol>/', views.TradingView.as_view(), name='trading'),
    path('order/cancel/<int:order_id>/', views.CancelOrderView.as_view(), name='cancel_order'),
]
#done