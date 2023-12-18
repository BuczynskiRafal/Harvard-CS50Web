import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User
from .models import Post


def index(request):
    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("content")
        if content:
            post = Post(author=request.user, content=content)
            post.save()
            return HttpResponseRedirect(reverse("index"))

    posts_list = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    return render(request, "network/index.html", {"posts": posts})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        post = Post(author=request.user, content=content)
        post.save()
        return redirect('index')
    else:
        return render(request, "network/new_post.html")


def all_posts(request):
    posts_list = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts_list, 10)

    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    return render(request, "network/all_posts.html", {"posts": posts})


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = user_profile.posts.all().order_by('-timestamp')
    followers = user_profile.followers.count()
    following = user_profile.following.all().count()
    
    is_following = False
    if request.user.is_authenticated and user_profile.followers.filter(id=request.user.id).exists():
        is_following = True

    context = {
        'user_profile': user_profile,
        'posts': posts,
        'followers': followers,
        'following': following,
        'is_following': is_following,
    }
    return render(request, 'network/profile.html', context)


@login_required
def edit_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id, author=request.user)
        data = json.loads(request.body)
        post.content = data['content']
        post.save()
        return JsonResponse({"message": "Post updated successfully."})

    return JsonResponse({"error": "Invalid request"}, status=400)


def toggle_like(request, post_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    post = get_object_or_404(Post, pk=post_id)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    
    return JsonResponse({"likes": post.likes.count()})


@login_required
def follow(request, username):
    if request.method == "POST":
        user_to_follow = get_object_or_404(User, username=username)
        
        if request.user != user_to_follow:
            if user_to_follow.followers.filter(id=request.user.id).exists():
                user_to_follow.followers.remove(request.user)
            else:
                user_to_follow.followers.add(request.user)
        
        return HttpResponseRedirect(reverse('profile', args=[username]))


@login_required
def following(request):
    user_following = request.user.following.all()
    posts = Post.objects.filter(author__in=user_following).order_by('-timestamp')
    return render(request, "network/following.html", {"posts": posts})
