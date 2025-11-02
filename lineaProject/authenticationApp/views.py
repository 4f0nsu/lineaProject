from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
import re
from .models import UserProfile

# Sign-up step1
import random
from django.utils import timezone
from datetime import timedelta
from .models import PendingUser
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

def generate_code():
    return str(random.randint(100000, 999999))  # 6 dígitos

def sign_up_step1(request):
    User = get_user_model()

    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Verifica se email ou username já existem
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este email já está registado. Use outro.")
            return redirect('sign_up_step1')

        # Campos obrigatórios
        if not all([email, password, confirm_password]):
            messages.error(request, "Preencha todos os campos.")
            return redirect('sign_up_step1')

        # Validar email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Email inválido.")
            return redirect('sign_up_step1')

        # Validar password
        if password != confirm_password:
            messages.error(request, "As passwords não coincidem.")
            return redirect('sign_up_step1')

        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            messages.error(request, "A password deve ter pelo menos 8 caracteres, um número e uma letra maiúscula.")
            return redirect('sign_up_step1')

        # Gerar código de verificação
        code = generate_code()
        expires_at = timezone.now() + timedelta(minutes=15)

        # Guardar PendingUser
        pending, created = PendingUser.objects.update_or_create(
            email=email,
            defaults={
                'password_hash': make_password(password),  # hash seguro
                'verification_code': code,
                'expires_at': timezone.now() + timedelta(minutes=15)
            }
        )

        # Enviar email
        send_mail(
            subject="Código de verificação",
            message=f"Seu código de verificação é: {code}",
            from_email="no-reply@teusite.com",
            recipient_list=[email],
            fail_silently=False,
        )

        # Redirecionar para página de verificação
        request.session['pending_email'] = email  # guardamos para o passo 2
        messages.success(request, "Código enviado para o seu email. Verifique e continue o registo.")
        return redirect('sign_up_verify_code')

    return render(request, 'authenticationApp/sign_up_step1.html')

def sign_up_verify_code(request):
    email = request.session.get('pending_email')
    if not email:
        messages.error(request, "Sessão expirada. Comece novamente.")
        return redirect('sign_up_step1')

    if request.method == "POST":
        input_code = request.POST.get('verification_code', '').strip()
        try:
            pending = PendingUser.objects.get(email=email)
            if pending.is_expired():
                pending.delete()
                messages.error(request, "O código expirou. Tente novamente.")
                return redirect('sign_up_step1')

            if input_code != pending.verification_code:
                messages.error(request, "Código inválido.")
                return redirect('sign_up_verify_code')

            # Código correto, avançar para Passo 2
            request.session['verified_email'] = email
            return redirect('sign_up_step2')

        except PendingUser.DoesNotExist:
            messages.error(request, "Código inválido. Comece novamente.")
            return redirect('sign_up_step1')

    return render(request, 'authenticationApp/sign_up_verify_code.html')

def sign_up_step2(request):
    email = request.session.get('verified_email')
    if not email:
        messages.error(request, "Sessão expirada. Comece novamente.")
        return redirect('sign_up_step1')

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        birth_date = request.POST.get('birth_date')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        postal_code = request.POST.get('postal_code', '')
        country = request.POST.get('country', '')
        user_type = request.POST.get('user_type', 'public')

        if not all([name, username]):
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return redirect('sign_up_step2')

        try:
            pending = PendingUser.objects.get(email=email)
            if pending.is_expired():
                pending.delete()
                messages.error(request, "O código expirou. Comece novamente.")
                return redirect('sign_up_step1')

            user = UserProfile(
                username=username,
                email=email,
                name=name,
                birth_date=birth_date,
                address=address,
                city=city,
                postal_code=postal_code,
                country=country,
                user_type=user_type
            )
            user.password = pending.password_hash  # hash já seguro
            user.save()

            # Remover PendingUser
            pending.delete()

            messages.success(request, "Conta criada com sucesso! Pode agora iniciar sessão.")
            return redirect('sign_in')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {e}")
            return redirect('sign_up_step2')

    return render(request, 'authenticationApp/sign_up_step2.html')


@csrf_protect
def sign_in(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Preencha ambos os campos.")
            return redirect('sign_in')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Previne sessão paralela antiga
            logout(request)
            login(request, user)
            request.session.set_expiry(3600)  # Sessão expira após 1h de inatividade
            messages.success(request, f"Bem-vindo {user.username}!")
            #return redirect('dashboard')
            
            # Redireciona para o feed de posts
            return redirect('posts:feed')  # <- aqui muda para a view do feed
        else:
            messages.error(request, "Credenciais inválidas. Tente novamente.")

    return render(request, 'authenticationApp/sign_in.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logout efetuado com sucesso.")
    return redirect('sign_in')

@login_required
def dashboard(request):
    return render(request, 'authenticationApp/dashboard.html')