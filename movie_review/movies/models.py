import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from accounts.models import UserProfile

# Create your models here.
class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, max_length=15, editable=False)
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=180, null=True, blank=True, unique_for_date='created_at')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')
    image = models.ImageField(upload_to='movies', default='movies/default_movie.jpg')
    director = models.CharField(max_length=100)
    year = models.CharField(max_length=4)
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.title} uploaded by {self.owner}"
    
    def average_rating(self):
        return self.ratings.aggregate(Avg('rating'))['rating__avg']
    

class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, max_length=15, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    rating = models.DecimalField(max_digits=4, decimal_places=2, default=1.0, validators=[MinValueValidator(1.00), MaxValueValidator(10.00)])

    def __str__(self) -> str:
        return f"Rating {self.rating} for {self.movie}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, max_length=15, editable=False)
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comment_profile')
    rate = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='rate', blank=True, null=True)
    comment = models.TextField()
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment {self.comment} for {self.movie}"
