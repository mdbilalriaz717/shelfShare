from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib import messages 
from .forms import BookForm
from .models import Book, UserProfile, BookRating
from django.core.paginator import Paginator


# Create your views here.

def viewBook_view(request):

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
        'query': None,  # no global search
        'is_search': False  # regular book viewing
    }

    return render(request, 'viewBook.html', context)
    


@login_required
def postBook_view(request):
    categories = ['Fiction', 'Non-fiction', 'Fantasy', 'Mystery', 'Science', 'History', 'Biography', 'Other']
    conditions = [
        ('new', 'New'),
        ('like-new', 'Like New'),
        ('good', 'Good'),
        ('acceptable', 'Acceptable'),
    ]

    edit = False
    book = None

    user_books = Book.objects.filter(posted_by=request.user)
    if user_books.exists():
        book = user_books.latest('book_id')  # Or use .first() or order by date field if available

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book_id = form.cleaned_data.get('book_id')
            if Book.objects.filter(book_id=book_id).exists():
                form.add_error('book_id', 'A book with this ID already exists. Please use a different Book ID.')

            else:
                new_book = form.save(commit=False)
                new_book.posted_by = request.user
                new_book.approved = False
                new_book.save()
                messages.success(request, "Book posted successfully! Waiting for admin approval.")
                return redirect('post_book')
        else:
            print(form.errors)
            messages.error(request, "Failed to post the book. Please correct the errors below.")
    else:
        form = BookForm()

    return render(request, 'postBook.html', {
        'form': form,
        'book': book,
        'categories': categories,
        'conditions': conditions,
        'edit': edit,
    })



@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id, posted_by=request.user)
    edit = True  # Important: You are editing

    categories = ['Fiction', 'Non-fiction', 'Fantasy', 'Mystery', 'Science', 'History', 'Biography', 'Other']
    conditions = [
    ('new', 'New'),
    ('like-new', 'Like New'),
    ('good', 'Good'),
    ('acceptable', 'Acceptable'),
]

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            updated_book = form.save(commit=False)
            updated_book.approved = False  # Needs re-approval after editing
            updated_book.save()
            messages.success(request, "Book updated successfully! Waiting for admin approval.")
            return redirect ('edit_book', book_id=book.book_id)  # Corrected: pass book_id
        else:
            messages.error(request, "Failed to update the book. Please correct the errors below.")
    else:
        form = BookForm(instance=book)

    return render(request, 'postBook.html', {
        'form': form,
        'book': book,
        'edit': edit,
        'categories': categories,
        'conditions': conditions,
    })



@user_passes_test(lambda u: u.is_superuser)
def pending_books(request):
    books = Book.objects.filter(approved=False)
    return render(request,'pending_books.html' ,{'books': books})



@user_passes_test(lambda u: u.is_superuser)
def approve_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    book.approved = True
    book.save()
    return redirect('pending_books')




@login_required
def BookDetails_view(request, book_id):
    book = get_object_or_404(Book, book_id=book_id, approved=True)

    # Ensure the user has a UserProfile
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    

    if request.method == 'POST':
        action = request.POST.get('action')

        # If user clicks "Download Book"
        if action == 'download':
            if user_profile.allowed_downloads > 0:
                # Decrease user's download count and increment book's download count
                user_profile.decrease_downloads()
                book.increment_download_count()

                # Mark that user has downloaded this book (optional: save in a download history model)
                user_profile.downloaded_books.add(book)  # if using a ManyToManyField

                messages.success(request, f"Book downloaded successfully! Remaining downloads: {user_profile.allowed_downloads}")
                return redirect('book_details', book_id=book.book_id)
            else:
                messages.error(request, "Please upload a book to continue downloading.")
                return redirect('book_details', book_id=book.book_id)
              
        # If user submits a rating
        elif action == 'rate':
            if book in user_profile.downloaded_books.all():
                rating = request.POST.get('rating')
                if rating:
                    # Check if user has already rated the book
                    if not BookRating.objects.filter(user=request.user, book=book).exists():
                        BookRating.objects.create(user=request.user, book=book, rating=float(rating))
                        book.update_rating()
                        messages.success(request, "Thank you for rating the book.")
                    else:
                        messages.error(request, "You have already rated this book.")
                else:
                    messages.error(request, "Please select a rating.")
            else:
                messages.error(request, "You must download the book before rating it.")
            return redirect('book_details', book_id=book.book_id)


    return render(request, 'BookDetails.html', {'book': book, 'user_profile': user_profile, 'rating_range': range(1, 6)})
