from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('viewBook/', views.viewBook_view, name='view_book'),
    path('bookDetails/<str:book_id>/', views.BookDetails_view, name='book_details'),
    path('postBook/', views.postBook_view, name='post_book'),
    path('edit/<str:book_id>/', views.edit_book, name='edit_book'),
    path('pending-books/', views.pending_books, name='pending_books'),  # For admin
    path('approve-book/<str:book_id>/', views.approve_book, name='approve_book'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)