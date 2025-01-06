from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, PostForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import authenticate, logout, login
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission, Group
from django.contrib import messages
from .models import Post
from django.views.generic import UpdateView
import requests
API_KEY = 'c6280cefba8c4eccaff85ab0426c8cc1'



def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.all()
    return user.user_permissions.all() | Permission.objects.filter(group__user=user)


# API integration ====================================

def news(request):
    url = f'https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    articles = data['articles']

    context = {
        'articles' : articles
    }

    return render(request, "main/news.html", context)





@login_required(login_url='/login')
def home(request):
    if request.method == "POST":
        post_id = request.POST.get("delete")
        post = Post.objects.filter(id=post_id).first()
        user_to_ban = request.POST.get("ban")
        if post and (request.user.has_perm("main.delete_post") or request.user == post.author):
            post.delete()
        elif user_to_ban and request.user.is_staff:
            user = User.objects.get(username=user_to_ban)
            if user.is_staff:
                messages.error(request, "You cannot ban this user.")
            else:
                group = Group.objects.get(name='default')
                group.user_set.remove(user)
                user.save()
                messages.success(request, "User account deactivated!")


    return render(request, "main/home.html",  {"posts": Post.objects.all(),  "request": request})
 
    
@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Check if the user is the author or has permission to edit the post
    if request.user != post.author and not request.user.has_perm("main.change_post"):
        messages.error(request, "You do not have permission to edit this post.")
        return redirect('home')

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('home')
    else:
        form = PostForm(instance=post)

    return render(request, "main/post_update.html", {"form": form})

def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            messages.success(request, "Account Created!")
            login(request, user)
            return redirect("/login")
    else:
        form = RegisterForm()

    return render(request, "registration/sign-up.html", {"form": form})


@login_required(login_url='/login')
@permission_required("main.add_post", login_url="/login", raise_exception=True)
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post Created!")
            return redirect("/home")
    else:
        form = PostForm()

    return render(request, "main/create-post.html", {"form": form})

# Update post logic +===================================

# Logout +=================================================
def custom_logout_view(request):
    logout(request)  
    return redirect('/login')  




