# Generated by Django 5.2 on 2025-05-14 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BooksDetails', '0005_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='downloaded_books',
            field=models.ManyToManyField(blank=True, related_name='downloaded_by', to='BooksDetails.book'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='uploaded_books',
            field=models.ManyToManyField(blank=True, related_name='uploaded_by', to='BooksDetails.book'),
        ),
    ]
