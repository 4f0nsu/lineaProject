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


@csrf_protect
def sign_up(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            birth_date = request.POST.get('birth_date')
            address = request.POST.get('address', '')
            city = request.POST.get('city', '')
            postal_code = request.POST.get('postal_code', '')
            country = request.POST.get('country', '')
            user_type = request.POST.get('user_type', 'public')

            # Validação de campos obrigatórios
            if not all([username, email, password, name]):
                messages.error(request, "Preencha todos os campos obrigatórios.")
                return redirect('sign_up')

            # Validação do email
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Por favor insira um email válido.")
                return redirect('sign_up')

            # Validação da password 
            if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
                messages.error(request, "A password deve ter pelo menos 8 caracteres, um número e uma letra maiúscula.")
                return redirect('sign_up')

            # Criar o utilizador 
            with transaction.atomic():  # garante rollback se algo falhar
                user = UserProfile.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    name=name,
                    birth_date=birth_date,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    country=country,
                    user_type=user_type
                )
                user.save()

            messages.success(request, "Conta criada com sucesso! Pode agora iniciar sessão.")
            return redirect('sign_in')

        except IntegrityError:
            messages.error(request, "O nome de utilizador ou email já está registado.")
            return redirect('sign_up')

        except Exception as e:
            # logging opcional
            print(f"[ERROR] Erro ao criar conta: {e}")
            messages.error(request, "Ocorreu um erro inesperado. Tente novamente.")
            return redirect('sign_up')

    return render(request, 'authenticationApp/sign_up.html')


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
            return redirect('dashboard')
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