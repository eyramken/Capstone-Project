from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.db.models import Avg, Count
from django.contrib import messages
from accounts.models import UserProfile
from movies.forms import CommentForm, MovieForm
from movies.models import Comment, Movie, Rating
from django.shortcuts import get_object_or_404


def index(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', '')
    category = request.GET.get('category', '')

    # Base queryset: filter by title if provided
    movies = Movie.objects.filter(title__icontains=query)

    # Apply category filter if present
    if category:
        movies = movies.filter(category__icontains=category)

    # Apply sorting logic
    if sort == 'popular':
        movies = movies.annotate(review_count=Count('reviews')).order_by('-review_count', 'title')
    elif sort == 'rating':
        movies = movies.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating', 'title')
    elif sort == 'latest':
        movies = movies.order_by('-created_at')
    else:
        # Default sort: alphabetical
        movies = movies.order_by('title')

    # Safely retrieve user profile only if logged in
    profile = None
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(person=request.user)
        except UserProfile.DoesNotExist:
            profile = None

    return render(request, 'index.html', {
        'movies': movies,
        'profile': profile
    })


@login_required(login_url='login')
def add_movie(request):
    profile = UserProfile.objects.get(person=request.user)

    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the movie
            movie = form.save(commit=False)
            movie.owner = request.user
            movie.slug = slugify(movie.title)
            movie.save()

            # Extract extra data
            rating_value = form.cleaned_data['rating']
            comment_text = form.cleaned_data['comment']

            # Create the rating
            rating = Rating.objects.create(
                movie=movie,
                rating=rating_value
            )

            # Create the comment
            comment = Comment.objects.create(
                person=request.user,
                movie=movie,
                profile=profile,
                rate=rating,
                comment=comment_text
            )

            messages.success(request, "Movie added!")
            return redirect('home')
        else:
            messages.error(request, "One or more input field error.")
    else:
        form = MovieForm()

    return render(request, 'add_movie.html', {
        'form': form,
        'profile': profile,
    })


@login_required(login_url='login')
def movie_review_page(request, slug, _id):
    movie = get_object_or_404(Movie, slug=slug, id=_id)
    profile = get_object_or_404(UserProfile, person=request.user)
    comments = Comment.objects.filter(movie=movie).select_related('profile', 'person', 'rate').order_by('-created')

    similar_movies = Movie.objects.filter(category=movie.category).exclude(id=movie.id)

    # Creating a review
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if comment.strip():
            rate = Rating.objects.create(movie=movie, rating=rating)

            Comment.objects.create(
                person=request.user,
                movie=movie,
                profile=profile,
                comment=comment,
                rate=rate
            )
            return redirect('review', movie.slug, movie.id)

    return render(request, 'review.html', {
        "movie": movie,
        "profile": profile,  # ✅ Pass the profile explicitly
        'comments': comments,
        "similar_movies": similar_movies,
    })


@login_required(login_url='login')
def update_movie(request, movie_slug, movie_id):
    movie = get_object_or_404(Movie, slug=movie_slug, id=movie_id)
    profile = get_object_or_404(UserProfile, person=request.user)

    if request.method == 'POST':
        form = MovieForm(request.POST or None, request.FILES or None, instance=movie, include_review_fields=False)

        if form.is_valid():
            updated_movie = form.save(commit=False)

            # Fallbacks for fields if left empty
            if not form.cleaned_data.get('title'):
                updated_movie.title = movie.title
            if not form.cleaned_data.get('director'):
                updated_movie.director = movie.director
            if not form.cleaned_data.get('year'):
                updated_movie.year = movie.year
            if not form.cleaned_data.get('category'):
                updated_movie.category = movie.category
            if not form.cleaned_data.get('image'):
                updated_movie.image = movie.image

            updated_movie.save()

            return redirect('review', updated_movie.slug, updated_movie.id)

    else:
        # No need to include rating/review on update
        form = MovieForm(instance=movie)

    return render(request, 'update_movie.html', {
        'form': form,
        'movie': movie,
        'profile': profile,
    })


@login_required(login_url='login')
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.person:
        messages.error(request, "You are not authorized to edit this comment.")
        return redirect('review', comment.movie.slug, comment.movie.id)

    profile = get_object_or_404(UserProfile, person=request.user)
    rating = comment.rate

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment, rating_initial=rating.rating if rating else None)
        if form.is_valid():
            updated_comment = form.save()

            rating_value = form.cleaned_data['rating']
            if rating:
                rating.rating = rating_value
                rating.save()
            else:
                new_rating = Rating.objects.create(movie=comment.movie, rating=rating_value)
                updated_comment.rate = new_rating
                updated_comment.save()

            messages.success(request, "Comment and rating updated.")
            return redirect('review', comment.movie.slug, comment.movie.id)
    else:
        form = CommentForm(instance=comment, rating_initial=rating.rating if rating else None)

    return render(request, "update_comment.html", {
        'form': form,
        'comment': comment,
        'profile': profile
    })


@login_required(login_url='login')
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Optional: Only allow the user who wrote the comment to delete it
    if request.user != comment.person:
        return redirect('home')  # or raise PermissionDenied

    if request.method == "POST":
        # Delete associated rating first (if any)
        if comment.rate:
            comment.rate.delete()

        # Now delete the comment
        comment.delete()

        return redirect('review', comment.movie.slug, comment.movie.id)

    return render(request, "delete_comment.html", {
        'comment': comment
    })


@login_required(login_url='login')
def delete_movie(request, slug, _id):
    movie = get_object_or_404(Movie, slug=slug, id=_id)

    if movie.owner != request.user:
        messages.error(request, "You are not authorized to delete this movie.")
        return redirect('home')

    # Delete instantly without confirmation page
    movie.delete()
    messages.success(request, "Movie deleted successfully.")
    return redirect('home')


    