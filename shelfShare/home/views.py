from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from BooksDetails.models import Book, UserProfile
from .forms import ContactMessageForm
from django.core.paginator import Paginator
from .models import ContactMessage


User = get_user_model()

# Create your views here
def home_view(request):
    books = Book.objects.filter(approved=True)

    title_query = request.GET.get('title', '').strip()
    author_query = request.GET.get('author', '').strip()
    category_query = request.GET.get('category', '').strip()

    if title_query:
        books = books.filter(book_title__icontains=title_query)
    if author_query:
        books = books.filter(author_name__icontains=author_query)
    if category_query:
        books = books.filter(category__icontains=category_query)

    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title_query': title_query,
        'author_query': author_query,
        'category_query': category_query,
    }

    return render(request, 'home.html', context)


@login_required
def profile_view(request):
    user = request.user
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    uploaded_books = Book.objects.filter(posted_by=user)
    downloaded_books = user_profile.downloaded_books.all()

    return render(request, 'Profile.html', {
        'user': user,
        'uploaded_books': uploaded_books,
        'downloaded_books': downloaded_books,
    })





def loading_view(request):

    return render(request, 'loading.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # Check if email is changing and is already taken
        if email != user.email and User.objects.filter(email=email).exists():
            messages.error(request, "Email address is already in use.")
            return render(request, 'EditProfile.html', {'user': request.user})
            

        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = email  # if you want username = email

        user.save()
        messages.success(request, "Profile updated successfully!")
        return render(request, 'EditProfile.html', {'user': request.user})
    else:
        return render(request, 'EditProfile.html' ,  {'user': request.user})  # Or your template name




@login_required
def change_password_view(request):
    if request.method == 'POST':
        # Debugging: Log the form data
        print("Form Submitted:")
        print("Current Password: ", request.POST.get('currentPassword'))
        print("New Password: ", request.POST.get('password1'))
        print("Confirm Password: ", request.POST.get('password2'))

        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        user = request.user

        # Check if the current password is correct
        if not user.check_password(current_password):
            messages.error(request, "Your current password is incorrect.")
            return redirect('profile')  # Redirect to show error

        # Check if the new passwords match
        if new_password != confirm_password:
            messages.error(request, "New password and Confirm password do not match.")
            return redirect('profile')

        # Check if the new password meets criteria (e.g., minimum 8 characters)
        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters long.")
            return redirect('profile')

        # Everything is okay, so set the new password
        user.set_password(new_password)
        user.save()  # Save the updated password to the database

        # Important: Keep the user logged in after password change
        update_session_auth_hash(request, user)

        messages.success(request, "Your password has been updated successfully.")
        return redirect('profile')  # Redirect after success to show the success message

    return render(request, 'profile.html')


    

@login_required
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')


        if name and email and message:
            contact_message = ContactMessage.objects.create(
                user=request.user,
                name=name,
                email=email,
                message=message
            )
            send_mail(
                subject=f"Hi {name}, We Received Your Message",
                message='Thank you for contacting us. We will get back to you shortly.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully. Please check your email.')
            return redirect('contact')
  # Replace with your actual URL name

    return render(request, 'test.html')



from django.shortcuts import redirect
from django.db.models import Q
from django.core.paginator import Paginator

def search_books(request):
    query = request.GET.get('q', '').strip()
    title = request.GET.get('title', '').strip()
    author = request.GET.get('author', '').strip()
    category = request.GET.get('category', '').strip()

    if query == '' and title == '' and author == '' and category == '':
        return redirect('view_book')  # no input, go to default view

    books = Book.objects.filter(approved=True)

    if query:
        books = books.filter(
            Q(book_id__icontains=query) |
            Q(book_title__icontains=query) |
            Q(author_name__icontains=query) |
            Q(category__icontains=query) |
            Q(book_condition__icontains=query)
        )
    if title:
        books = books.filter(book_title__icontains=title)
    if author:
        books = books.filter(author_name__icontains=author)
    if category:
        books = books.filter(category__icontains=category)

    paginator = Paginator(books, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'viewBook.html', {
        'page_obj': page_obj,
        'query': query,
        'title_query': title,
        'author_query': author,
        'category_query': category,
        'is_search': True
    })

