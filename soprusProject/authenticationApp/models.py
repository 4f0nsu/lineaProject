from django.contrib.auth.models import AbstractUser
from django.db import models

# Modelo customizado de utilizador
class UserProfile(AbstractUser):
    class UserType(models.TextChoices):
        PUBLIC = 'public', 'Public'
        ARTIST = 'artist', 'Artist'
        ADMIN = 'admin', 'Admin'  # podes expandir no futuro

    # Campos personalizados
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=120, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.PUBLIC)
    profile_picture_url = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # O AbstractUser já tem: username, password, is_active, is_staff, etc.
    REQUIRED_FIELDS = ['email', 'name']

    def __str__(self):
        return self.username
