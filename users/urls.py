from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
urlpatterns = [
    path('register/', views.send_confirmation_email, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('confirm-email/', views.confirm_email, name='confirm_email'),
    path('complete-registration/', views.complete_registration, name='complete_registration'),
    path('post-login/', views.post_login_redirect, name='post_login_redirect'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('resend-confirmation-code/', views.resend_confirmation_code, name='resend_confirmation_code'),  # Новий маршрут
    path("2fa/", views.two_factor_setup, name="two_factor_setup"),
    path("verify_2fa/", views.verify_2fa, name="verify_2fa"),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('update-phone/', views.update_phone, name='update_phone'),
    path('update-country/', views.update_country, name='update_country'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)