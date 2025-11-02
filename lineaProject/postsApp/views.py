from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from .models import Post, Like, Comment, Media
from .forms import PostForm, CommentForm

# Create your views here.


# FEED PRINCIPAL (posts mais recentes de todos)
@method_decorator(login_required, name='dispatch')
class FeedView(ListView):
    model = Post
    template_name = 'postsApp/feed.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        # Mostra posts de todos os utilizadores (podes filtrar por quem segues depois)
        return Post.objects.select_related('creator').prefetch_related('media', 'likes', 'comments')



# POSTS DE UM UTILIZADOR ESPECÍFICO
@method_decorator(login_required, name='dispatch')
class UserPostsView(ListView):
    model = Post
    template_name = 'postsApp/user_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        username = self.kwargs.get('username')
        return Post.objects.filter(creator__username=username).select_related('creator').prefetch_related('media')



# DETALHES DE UM POST (com comentários)
@method_decorator(login_required, name='dispatch')
class PostDetailView(DetailView):
    model = Post
    template_name = 'postsApp/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('user')
        context['liked'] = Like.objects.filter(user=self.request.user, post=self.object).exists()
        return context



# CRIAR UM NOVO POST
@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'postsApp/post_form.html'
    success_url = reverse_lazy('posts:feed')

    def form_valid(self, form):
        # Define o criador do post
        form.instance.creator = self.request.user
        response = super().form_valid(form)

        # Processa múltiplos arquivos enviados
        files = self.request.FILES.getlist('media_files')
        for f in files:
            Media.objects.create(
                post=self.object,
                file_url=f,  # ou file=f se o campo Media for FileField/ImageField
                media_type=form.cleaned_data['content_type']
            )

        messages.success(self.request, "Post criado com sucesso!")
        return response
    


# LIKE / UNLIKE POST (AJAX)
@login_required
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    # Retorna resposta JSON (para usar com JS/AJAX)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})
    return redirect('posts:detail', pk=pk)



# ADICIONAR COMENTÁRIO
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                post=post,
                user=request.user,
                text=form.cleaned_data['text']
            )
            messages.success(request, "Comentário adicionado!")
        else:
            messages.error(request, "Erro ao adicionar comentário.")
    return redirect('posts:detail', pk=pk)



# APAGAR POST (apenas o autor)
@method_decorator(login_required, name='dispatch')
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'postsApp/post_confirm_delete.html'
    success_url = reverse_lazy('posts:feed')

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.creator != request.user:
            messages.error(request, "Não tens permissão para apagar este post.")
            return redirect('posts:detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)
