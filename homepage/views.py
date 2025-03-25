from django.shortcuts import render

from users.models import UserProfile


def home(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            is_2fa_authenticated = user_profile.is_2fa_authenticated
        except UserProfile.DoesNotExist:
            is_2fa_authenticated = False
    else:
        is_2fa_authenticated = False

    return render(request, "homepage/index.html", {
        "is_2fa_authenticated": is_2fa_authenticated
    })

def error_view(request, exception=None, status=500, message="Щось пішло не так"):
    return render(request, 'homepage/error.html', {
        'status_code': status,
        'message': message
    }, status=status)

def custom_404(request, exception):
    return error_view(request, exception, status=404, message="Сторінка не знайдена")

def custom_500(request):
    return error_view(request, status=500, message="Внутрішня помилка сервера")

def custom_403(request, exception):
    return error_view(request, exception, status=403, message="Доступ заборонено")

def custom_400(request, exception):
    return error_view(request, exception, status=400, message="Неправильний запит")
