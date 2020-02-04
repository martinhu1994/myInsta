from annoying.decorators import ajax_request
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from insta_app.models import Post, Like, InstaUser, UserConnection, Comment
from insta_app.forms import CustomUserCreationForm

class HelloWord(TemplateView):
    template_name = 'example.html'


class PostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'index.html'
    login_url = 'login'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return 
        
        current_user = self.request.user
        followings = set()
        for conn in UserConnection.objects.filter(creator=current_user).select_related('following'):
            followings.add(conn.following)
        return Post.objects.filter(author__in=followings)


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    fields = ['title', 'image']
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['title']
    login_url = 'login'


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    login_url = 'login'
    #success_url = reverse_lazy("posts")

    def get_success_url(self):
        return reverse_lazy("user_detail", args=[self.request.user.pk])


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')


class UserDetailView(DetailView):
    model = InstaUser
    template_name = 'user_detail.html'


@ajax_request
def addLike(request):
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user)
        like.save()
        result = 1
    except Exception as e:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        result = 0

    return {
        'result': result,
        'post_pk': post_pk
    }


@ajax_request
def toggleFollow(request):
    follow_user_pk = request.POST.get('follow_user_pk')
    operation_type = request.POST.get('type')
    
    follow_user = InstaUser.objects.get(pk=follow_user_pk)
    try:
        if operation_type == 'follow':
            conn = UserConnection(creator=request.user, following=follow_user)
            conn.save()
        else:
            conn = UserConnection.objects.get(creator=request.user, following=follow_user)
            conn.delete()
        result = 1
    except Exception as e:
        print(e)
        result = 0
    
    return {
        'creator_pk': request.user.pk,
        'follow_user_pk': follow_user_pk,
        'type': operation_type
    }


@ajax_request
def addComment(request):
    comment_text = request.POST.get('comment_text')
    post_pk = request.POST.get('post_pk')
    
    post = Post.objects.get(pk=post_pk)
    commenter_info = {}
    try:
        comment = Comment(post=post, user=request.user, comment=comment_text)
        comment.save()
        commenter_info['username'] = request.user.username
        commenter_info['comment_text'] = comment_text
        result = 1
    except Exception as e:
        print(e)
        result = 0
    
    return {
        'result': result,
        'post_pk': post_pk,
        'commenter_info': commenter_info
    }


def redirection(request):
    if request.user.is_authenticated:
        response = redirect('posts')
    else:
        response = redirect('login')
    return response