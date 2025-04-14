from django import forms
from .models import Movie, Comment
from django.core.exceptions import ValidationError
import datetime

common_class = "mb-5 mt-2 text-gray-600 focus:outline-none focus:border focus:border-pgreen font-normal w-full h-10 flex items-center pl-3 text-sm border-gray-300 rounded border"

def validate_image(value):
    valid_image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    if not any(value.name.lower().endswith(ext) for ext in valid_image_extensions):
        raise ValidationError("Invalid image format. Only .jpg, .jpeg, .png, .gif, and .bmp are allowed.")


class MovieForm(forms.ModelForm):
    rating = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False,  # Make optional
        min_value=1.0,
        max_value=10.0,
        error_messages={
            'required': 'Please provide a rating between 1.0 and 10.0',
            'min_value': 'Minimum rating is 1.0',
            'max_value': 'Maximum rating is 10.0'
        }
    )

    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': "mt-2 bg-pgray/50 focus:outline-none focus:border focus:border-pgreen font-normal w-full p-3 text-sm border-gray-300 rounded border resize-none",
            'placeholder': "Write your thoughts about the movie...",
            'rows': 4
        }),
        label='Review',
        required=False  # Make optional
    )

    def __init__(self, *args, **kwargs):
        self.include_review_fields = kwargs.pop('include_review_fields', True)
        super(MovieForm, self).__init__(*args, **kwargs)

        # Only include rating and comment if needed
        if not self.include_review_fields:
            self.fields.pop('rating', None)
            self.fields.pop('comment', None)

        current_year = datetime.date.today().year
        year_choices = [(str(y), str(y)) for y in range(current_year, 1900, -1)]

        CHOICES = (
            ('Action', 'Action'), ('Comedy', 'Comedy'), ('Sci-Fi', 'Sci-Fi'),
            ('Adventure', 'Adventure'), ('Drama', 'Drama'), ('Horror', 'Horror'),
            ('Romance', 'Romance'), ('Thriller', 'Thriller'), ('Fantasy', 'Fantasy'),
            ('Mystery', 'Mystery'), ('Animation', 'Animation'),
        )

        self.fields['title'].widget.attrs.update({'class': common_class, 'placeholder': 'Enter movie title'})
        self.fields['director'].widget.attrs.update({'class': common_class, 'placeholder': 'Enter movie director'})
        self.fields['image'].widget.attrs.update({'class': common_class, 'placeholder': 'Upload movie poster'})
        self.fields['category'].widget = forms.Select(choices=CHOICES, attrs={'class': common_class})
        self.fields['year'].widget = forms.Select(choices=year_choices, attrs={'class': common_class})

        self.fields['image'].validators.append(validate_image)
        self.fields['image'].required = True

    class Meta:
        model = Movie
        fields = ('title', 'image', 'director', 'year', 'category', 'rating', 'comment')


class CommentForm(forms.ModelForm):
    rating = forms.FloatField(
        min_value=1.0,
        max_value=10.0,
        required=True,
        widget=forms.NumberInput(attrs={
            'step': 0.1,
            'class': "mt-2 w-full h-10 bg-pgray/50 text-gray-700 rounded border border-gray-300 pl-3 text-sm focus:outline-none focus:border-pgreen"
        }),
        label='Your Rating',
        error_messages={
            'required': 'Please provide a rating between 1.0 and 10.0',
            'min_value': 'Minimum rating is 1.0',
            'max_value': 'Maximum rating is 10.0'
        }
    )

    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': "mt-2 bg-pgray/50 focus:outline-none focus:border focus:border-pgreen font-normal w-full p-3 text-sm border-gray-300 rounded border resize-none",
                'placeholder': "Edit your comment...",
                'rows': 5
            })
        }
        labels = {
            'comment': 'Your Review'
        }

    def __init__(self, *args, **kwargs):
        rating_initial = kwargs.pop('rating_initial', None)
        super().__init__(*args, **kwargs)

        if rating_initial is not None:
            self.fields['rating'].initial = rating_initial