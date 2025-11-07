from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Conversation, Message
from authenticationApp.models import UserProfile  # importa o teu modelo personalizado

# Create your views here.
@login_required
def user_list_view(request):
    # Pega todos os utilizadores exceto o logado
    users = UserProfile.objects.exclude(id=request.user.id)
    return render(request, 'messagesApp/user_list.html', {'users': users})
@login_required
def inbox(request):
    """
    Mostra todas as conversas do utilizador atual.
    Ordenadas pela data da última mensagem.
    """
    user = request.user
    conversations = Conversation.objects.filter(participants=user).order_by('-updated_at')
    return render(request, 'messagesApp/inbox.html', {'conversations': conversations})


@login_required
def conversation_view(request, username):
    """
    Mostra a conversa entre o utilizador atual e outro utilizador.
    Permite enviar novas mensagens.
    """
    user = request.user
    other_user = get_object_or_404(UserProfile, username=username)

    # Tenta encontrar uma conversa existente
    conversation = Conversation.objects.filter(participants=user).filter(participants=other_user).first()

    # Se não existir, cria uma nova
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(user, other_user)
        conversation.save()

    # Marca as mensagens recebidas como lidas
    conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)


    # Enviar mensagem
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=user,
                content=content
            )
            conversation.save()  # atualiza o updated_at
            return redirect('messages:conversation', username=other_user.username)
        else:
            messages.error(request, "A mensagem não pode estar vazia.")

    # Obter mensagens da conversa
    msgs = conversation.messages.all().order_by('timestamp')

    return render(request, 'messagesApp/conversation.html', {
        'conversation': conversation,
        'messages': msgs,
        'other_user': other_user,
    })