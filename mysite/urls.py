from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from users import views as user_views
from trade import views as trade_views
from django.views.i18n import JavaScriptCatalog

# URL-адреси, які не потребують перекладу
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Для перемикання мов
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    # Можна додати інші URL, які не потребують перекладу (наприклад, API)
]

# URL-адреси, які будуть перекладатися
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')), 
    path('accounts/', include('users.urls')), 
    path('auth/', include('social_django.urls', namespace='social')),
    path('profile/', user_views.user_profile, name='user-profile'),
    path('wallet/', trade_views.WalletView.as_view(), name='wallet'),
    path('trade/', include('trade.urls', namespace='trade')),
    prefix_default_language=False  # Не додавати префікс для мови за замовчуванням
)

handler404 = 'homepage.views.custom_404'
handler500 = 'homepage.views.custom_500'
handler403 = 'homepage.views.custom_403'
handler400 = 'homepage.views.custom_400' 