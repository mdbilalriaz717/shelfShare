from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.loading_view, name='loading'),
    path('home/', views.home_view,  name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/editProfile/', views.update_profile, name='edit_profile'),
    path('profile/changePassword/', views.change_password_view, name='change_password'),
    path('books/', include('BooksDetails.urls')),
    path('contact/', views.contact_view, name='contact'),
    path('search/', views.search_books, name='search_books'),
    
]