import pyotp
from PIL import Image
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .models import EmailConfirmation
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import User
from .forms import UpdateProfileForm
import random
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import UserProfile
from pyotp import TOTP
from django.contrib import messages
import qrcode
from io import BytesIO
import base64, pyotp
from .utils import upload_to_imgbb
import requests
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask

# Видалення всіх записів
# EmailConfirmation.objects.all().delete()


def resend_confirmation_code(request):
    email = request.session.get('pending_email')
    if not email:
        return redirect('register') 

    try:
        confirmation = EmailConfirmation.objects.get(email=email)
        confirmation.confirmation_code = str(random.randint(100000, 999999)) 
        confirmation.save()

        send_mail(
            'Confirmation Code',
            f'Your new confirmation code is: {confirmation.confirmation_code}',
            'bitsim.confirm@gmail.com',
            [email],
        )
        return redirect('confirm_email') 
    except EmailConfirmation.DoesNotExist:
        return redirect('register') 


def send_confirmation_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        confirmation, created = EmailConfirmation.objects.get_or_create(email=email)
        if not created and confirmation.is_confirmed:
            return render(request, 'email_already_confirmed.html')

        confirmation.confirmation_code = str(random.randint(100000, 999999))
        confirmation.is_confirmed = False
        confirmation.save()
        request.session['pending_email'] = email

        html_content = render_to_string('users/email.html', {
            'confirmation_code': confirmation.confirmation_code,
            'email': confirmation.email
        })

        subject = 'Код підтвердження'
        from_email = 'bitsim.confirm@gmail.com'
        to_email = [email]

        email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()
        return redirect('confirm_email')
    return render(request, 'users/login_register/register.html')


def confirm_email(request):
    email = request.session.get('pending_email')
    if not email:
        return redirect('send_confirmation_email')

    error_message = None
    if request.method == 'POST':
        code = ''.join([
            request.POST.get(f'code{i}', '') for i in range(1, 7)
        ])
        try:
            confirmation = EmailConfirmation.objects.get(email=email, confirmation_code=code)

            if confirmation.created_at + timedelta(minutes=10) < now():
                return render(request, 'users/confirmation_expired.html')
            confirmation.is_confirmed = True
            confirmation.save()

            request.session['confirmed_email'] = email
            del request.session['pending_email']
            return redirect('complete_registration')
        except EmailConfirmation.DoesNotExist:
            error_message = "Неправильний код підтвердження. Спробуйте ще раз."

    return render(request, 'users/confirm_email.html', {'email': email, 'error_message': error_message})


def complete_registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        email = request.session.get('confirmed_email')
        if not email:
            return redirect('send_confirmation_email') 

        if User.objects.filter(username=username).exists():
            messages.error(request, "Цей username вже зайнятий. Будь ласка, оберіть інший.")
            return render(request, 'users/login_register/complete_registration.html', {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
            })

        user = User.objects.create_user(
            username=username,
            email=email, 
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.backend = 'django.contrib.auth.backends.ModelBackend'

        del request.session['confirmed_email']

        login(request, user)  
        return redirect('profile') 

    return render(request, 'users/login_register/complete_registration.html')
def profile_update_required(user):
    """
    Перевіряє, чи заповнив користувач обов'язкові поля профілю.
    """
    return not user.first_name or not user.last_name
@login_required
def post_login_redirect(request):
    """
    Перевірка після логіну: якщо дані профілю н■е заповнені, перенаправити користувача.
    """
    if profile_update_required(request.user):
        return redirect('update_profile')  
    return redirect('homepage')


@login_required
def update_profile(request):
    """
    Відображення форми для оновлення профілю.
    """
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, 'users/profile/update_profile.html', {'form': form})
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user_profile = UserProfile.objects.get(user=user)

            if user_profile.is_2fa_authenticated:
                request.session['pre_authenticated_user_id'] = user.id
                print(request.session.get('pre_authenticated_user_id'))
                return redirect('verify_2fa')

            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login_register/login.html', {'form': form})


def verify_2fa(request):
    if request.method == 'POST':
        user_id = request.session.get('pre_authenticated_user_id')
        if not user_id:
            return redirect('login')

        user = User.objects.get(id=user_id)
        user_profile = UserProfile.objects.get(user=user)
        totp = TOTP(user_profile.totp_secret)
        code = request.POST.get('2fa_code')

        if totp.verify(code):
            backend = user.backend if hasattr(user, 'backend') else 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend=backend)
            del request.session['pre_authenticated_user_id']
            return redirect('profile')
        else:
            messages.error(request, "Неправильний код 2FA. Спробуйте ще раз.")

    return render(request, 'users/2fa/verify_2fa.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('homepage')


@login_required
def user_profile(request):
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=request.user)
        is_2fa_authenticated = user_profile.is_2fa_authenticated
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
        is_2fa_authenticated = False

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            profile_picture = request.FILES.get('profile_picture')

            if profile_picture:
                try:
                    image_url = upload_to_imgbb(profile_picture)
                    user_profile.profile_picture = image_url 
                    user_profile.save()
                    messages.success(request, "Ваше фото профілю оновлено!")
                except Exception as e:
                    messages.error(request, f"Сталася помилка під час завантаження фото: {e}")
            else:
                messages.error(request, "Будь ласка, виберіть файл для завантаження.")

            return redirect('profile') 
        else:
            messages.error(request, "Сталася помилка під час оновлення фото.",request.FILES)
    else:
        form = ProfileUpdateForm(instance=user_profile)

    return render(request, "users/profile/profile.html", {
        "is_2fa_authenticated": is_2fa_authenticated,
        "user": user,
        "form": form
    })



@login_required
def two_factor_setup(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if not user_profile.totp_secret:
        user_profile.generate_totp_secret()

    totp = pyotp.TOTP(user_profile.totp_secret)
    qr_uri = totp.provisioning_uri(request.user.username, issuer_name="BitSim")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_uri)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=RadialGradiantColorMask(center_color=(10, 140, 15), edge_color=(0, 0, 0)),
    )

    logo_url = "https://i.ibb.co/t84hck7/a-modern-illustration-of-a-green-dollar-bso2h-Z2f-Tf-Ggs5-Bbf-OLBQ-CZCdl-B9x-Sp-ONKltnvko-MIg-remove.png" 
    try:
        response = requests.get(logo_url)
        response.raise_for_status() 
        logo = Image.open(BytesIO(response.content))

        logo_size = (img.size[0] // 1, img.size[1] // 4) 
        logo.thumbnail(logo_size)

        img_center = (
            (img.size[0] - logo.size[0]) // 2,
            (img.size[1] - logo.size[1]) // 2,
        )
        img.paste(logo, img_center, logo if logo.mode == "RGBA" else None)
    except requests.RequestException as e:
        print(f"Помилка завантаження логотипу: {e}")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    if request.method == "POST":
        token = request.POST.get("token")
        totp = TOTP(user_profile.totp_secret)

        if totp.verify(token):
            user_profile.is_2fa_authenticated = True
            user_profile.save()
            messages.success(request, "2FA успішно активовано!")
            return redirect("homepage")
        else:
            messages.error(request, "Невірний код. Спробуйте ще раз.")

    return render(request, "users/2fa/two_factor_setup.html", {
        "qr_code_base64": qr_code_base64,
        "user_profile": user_profile,
    })
@login_required
def delete_account(request):
    user = request.user

    EmailConfirmation.objects.filter(email=user.email).delete()
    user.delete()
    request.session.flush()

    return JsonResponse({'message': 'Акаунт успішно видалено'}, status=200)

@login_required
def update_phone(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if phone_number:
            request.user.profile.phone_number = phone_number
            request.user.profile.save()
            return JsonResponse({"message": "Номер телефону оновлено успішно!"})
    return JsonResponse({"error": "Некоректний номер телефону."}, status=400)

@login_required
def update_country(request):
    if request.method == 'POST':
        country = request.POST.get('country')
        if country:
            request.user.profile.country = country
            request.user.profile.save()
            return JsonResponse({"message": "Країна оновлена успішно!"})
    return JsonResponse({"error": "Некоректне значення країни."}, status=400)