from django.contrib import admin
from .models import Book  # Adjust import path if necessary

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'book_title', 'author_name', 'posted_by', 'posted_date', 'approved')
    list_filter = ('approved', 'book_condition', 'category')
    search_fields = ('book_title', 'author_name', 'book_id')