from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import BlogPage, BlogComment
from .forms import BlogCommentForm, LoginForm, RegisterForm


@require_POST
@csrf_protect
def add_comment(request, page_id):
    page = get_object_or_404(BlogPage, id=page_id)
    form = BlogCommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.page = page
        if request.user.is_authenticated:
            comment.user = request.user
            if not comment.author_name:
                comment.author_name = request.user.get_full_name() or request.user.username
            if not comment.author_email and request.user.email:
                comment.author_email = request.user.email
        comment.is_approved = True
        comment.save()
        messages.success(request, "Your comment has been posted successfully!")
    else:
        messages.error(request, "Please fill in all required fields to submit your comment.")

    # Redirect back to the post's comment section
    return redirect(page.url + "#comments")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    next_url = request.GET.get("next") or request.POST.get("next") or "/"

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()

    return render(
        request,
        "auth/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome to HakimBlog, {user.first_name or user.username}.")
            return redirect("/")
    else:
        form = RegisterForm()

    return render(
        request,
        "auth/register.html",
        {"form": form},
    )


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect("/")
