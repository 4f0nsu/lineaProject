from django.db import models
from django.conf import settings

# Create your models here.
User = settings.AUTH_USER_MODEL


class Conversation(models.Model):
    """
    Representa uma conversa entre dois utilizadores.
    É criada automaticamente quando o primeiro envia uma mensagem.
    """
    participants = models.ManyToManyField(User, related_name='conversations')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        usernames = [user.username for user in self.participants.all()]
        return f"Conversa entre {', '.join(usernames)}"

    def last_message(self):
        return self.messages.order_by('-timestamp').first()


class Message(models.Model):
    """
    Uma mensagem enviada entre dois utilizadores.
    """
    conversation = models.ForeignKey(
        Conversation, related_name='messages', on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User, related_name='sent_messages', on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"