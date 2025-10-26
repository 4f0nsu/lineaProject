from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import UserProfile

# Create your views here.
@csrf_protect
def sign_up(request):
    if request.method == "POST":
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        birth_date = request.POST.get('birth_date')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        user_type = request.POST.get('user_type', 'public')

        # Verificações simples
        if UserProfile.objects.filter(username=username).exists():
            messages.error(request, "Esse nome de utilizador já existe.")
            return redirect('sign_up')

        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Esse email já está registado.")
            return redirect('sign_up')

        # Criar utilizador com hash de password automática
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

    return render(request, 'authenticationApp/sign_up.html')

@csrf_protect
def sign_in(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
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
