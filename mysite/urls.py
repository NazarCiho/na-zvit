from django.contrib import admin
from django.urls import path, include
from users import views as user_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),  # Головна сторінка
    path('accounts/', include('users.urls')),  # URL для реєстрації та логіну
    path('auth/', include('social_django.urls', namespace='social')),
    path('profile/', user_views.user_profile, name='user-profile'),
    path('trade/', include('trade.urls')),

]


handler404 = 'homepage.views.custom_404'
handler500 = 'homepage.views.custom_500'
handler403 = 'homepage.views.custom_403'
handler400 = 'homepage.views.custom_400'
