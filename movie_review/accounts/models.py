from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=15)
    person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    # bio = models.TextField(max_length=500, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars', blank=False, null=False)

    def __str__(self):
        return f"{self.person.username}'s Profile"



    