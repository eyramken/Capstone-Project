from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from movies.models import Comment, Movie
from .models import UserProfile
from django.contrib import messages
# Create your views here.

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Invalid login
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('login')


def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name', 'unknown')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Check if passwords match
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        # Check if username is taken
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already in use. Please choose another.")
            return render(request, 'register.html')

        # Optional: Check if email is taken
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'register.html')

        # Check if avatar is provided
        if 'avatar' not in request.FILES or not request.FILES.get('avatar'):
            messages.error(request, "Profile picture is required.")
            return render(request, 'register.html')

        avatar = request.FILES['avatar']

        try:
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            # Create the user profile
            profile = UserProfile.objects.create(person=user, avatar=avatar)

            # Log in the user and redirect
            login(request, user)
            return redirect('home')

        except IntegrityError:
            messages.error(request, "Something went wrong. Please try again.")
            return render(request, 'register.html')

    return render(request, 'register.html')


def user_profile(request):  
    user = request.user
    profile = UserProfile.objects.get(person=user)

    # Movies uploaded by the user
    user_movies = Movie.objects.filter(owner=user)

    # Comments made by the user
    user_reviews = Comment.objects.filter(person=user)

    return render(request, 'profile.html', {
        'profile': profile,
        'user_movies': user_movies,
        'user_reviews': user_reviews,
    })