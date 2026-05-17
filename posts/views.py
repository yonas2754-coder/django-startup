# posts/views.py
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Post, Comment
from .forms import PostForm, CommentForm, UserRegistrationForm


class PostListView(ListView):
    """List all posts (newest first)"""
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']


class PostDetailView(DetailView):
    """View a single post + handle comments"""
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        post = self.get_object()
        if request.user.role not in ['staff', 'director']:
            messages.error(request, "Only Staff and Directors can comment.")
            return redirect('post_detail', pk=post.pk)

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
        else:
            messages.error(request, "Failed to add comment. Please check the form.")
            
        return redirect('post_detail', pk=post.pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create a new post (Director & Staff only)"""
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('post_list')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == 'manager':
            messages.error(request, "Managers cannot create posts.")
            return redirect('post_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Edit a post (Director can edit any, Staff can edit own)"""
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('post_list')

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        is_owner = post.author == request.user
        if request.user.role == 'director' or (request.user.role == 'staff' and is_owner):
            return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "You don't have permission to edit this post.")
        return redirect('post_detail', pk=post.pk)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a post (Director can delete any, Staff can delete own)"""
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        is_owner = post.author == request.user
        if request.user.role == 'director' or (request.user.role == 'staff' and is_owner):
            return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "You don't have permission to delete this post.")
        return redirect('post_detail', pk=post.pk)


def register_view(request):
    """User registration with auto-login"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created! Welcome, {user.username}.")
            return redirect('post_list')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'registration/register.html', {'form': form})