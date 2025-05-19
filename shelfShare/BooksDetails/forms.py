from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'book_id',
            'book_title',
            'edition',
            'author_name',
            'publication_year',
            'category',  # dropdown
            'custom_category',  # text field (if Other)
            'book_condition',  # dropdown
            'description',
            'book_cover_image',
            'book_document',
            'email',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'custom_category': forms.TextInput(attrs={'placeholder': 'Enter custom category'}),
        }
