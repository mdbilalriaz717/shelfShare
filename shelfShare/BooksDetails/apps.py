from django.apps import AppConfig


class BooksdetailsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BooksDetails'

    def ready(self):
        import BooksDetails.signals 
