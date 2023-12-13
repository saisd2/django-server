from .models import Upload
from django import forms

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['title', 'caption', 'category', 'image', 'average_rating', 'total_ratings']