from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

class Book(models.Model):
    book_id = models.CharField(max_length=20, primary_key=True)
    book_title = models.CharField(max_length=255)
    edition = models.CharField(max_length=50, blank=True, null=True)
    author_name = models.CharField(max_length=255)
    publication_year = models.PositiveIntegerField()
    
    category = models.CharField(max_length=100)  # Changed to free text
    custom_category = models.CharField(max_length=100, blank=True, null=True)  # <-- To store user's custom input
    
    BOOK_CONDITIONS = [
        ('new', 'New'),
        ('like-new', 'Like New'),
        ('good', 'Good'),
        ('acceptable', 'Acceptable'),
    ]
    book_condition = models.CharField(max_length=50, choices=BOOK_CONDITIONS)
    
    description = models.TextField()
    book_cover_image = models.ImageField(upload_to='book_covers/')
    book_document = models.FileField(upload_to='book_documents/', blank=True, null=True)
    email = models.EmailField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_date = models.DateTimeField(auto_now_add=True)
    no_of_downloads = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)

    approved = models.BooleanField(default=False) 

    def update_rating(self, new_rating):
        print(f"Updating rating to: {new_rating}")
        self.rating = new_rating
        self.save()

    def increment_download_count(self):
        print("Incrementing download count")
        self.no_of_downloads += 1
        self.save()

    def update_rating(self):
        average = BookRating.objects.filter(book=self).aggregate(Avg('rating'))['rating__avg']
        self.rating = average if average else 0.0
        self.save()

    def __str__(self):
        return self.book_title






class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allowed_downloads = models.IntegerField(default=2)
    uploaded_books = models.ManyToManyField(Book, related_name='uploaded_by', blank=True)
    downloaded_books = models.ManyToManyField(Book, related_name='downloaded_by', blank=True)

    def increase_downloads(self, amount):
        self.allowed_downloads += amount
        self.save()

    def decrease_downloads(self):
        if self.allowed_downloads > 0:
            self.allowed_downloads -= 1
            self.save()

    def reset_downloads(self):
        self.allowed_downloads = 2  # Reset downloads after book upload
        self.save()



# models.py

class BookRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.FloatField()

    class Meta:
        unique_together = ('user', 'book')  # Prevent duplicate ratings

    def __str__(self):
        return f'{self.user.username} rated {self.book.book_title} - {self.rating}'
