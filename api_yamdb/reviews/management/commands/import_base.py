"""Модуль для импорта данных из CSV файлов в модели Django."""

from csv import DictReader

from django.core.management.base import BaseCommand

from api_yamdb.settings import BASE_DIR
from reviews.models import Category, Comments, Genre, GenreTitle, Review, Title
from users.models import User


class Command(BaseCommand):
    """Команда для импорта данных из CSV."""

    help = 'Импорт данных из csv файлов'

    def import_user(self):
        """Импортирует данные для модели User."""
        if User.objects.exists():
            print('Данные для User уже загружены')
        else:
            with open(BASE_DIR / 'static/data/users.csv',
                      encoding='utf8') as file:
                reader = DictReader(file)
                users_to_create = [
                    User(id=row['id'], username=row['username'],
                         email=row['email'], role=row['role'], bio=row['bio'],
                         first_name=row['first_name'],
                         last_name=row['last_name'])
                    for row in reader]
                User.objects.bulk_create(users_to_create)
                print('Данные для User загружены')

    def import_genre(self):
        """Импортирует данные для модели Genre."""
        if Genre.objects.exists():
            print('Данные для Genre уже загружены')
        else:
            with open(BASE_DIR / 'static/data/genre.csv',
                      encoding='utf8') as file:
                reader = DictReader(file)
                genres_to_create = [
                    Genre(id=row['id'], name=row['name'], slug=row['slug'])
                    for row in reader]
                Genre.objects.bulk_create(genres_to_create)
                print('Данные для Genre загружены')

    def import_category(self):
        """Импортирует данные для модели Category."""
        if Category.objects.exists():
            print('Данные для Category уже загружены')
        else:
            with open(BASE_DIR / 'static/data/category.csv',
                      encoding='utf8') as file:
                reader = DictReader(file)
                categories_to_create = [
                    Category(id=row['id'], name=row['name'], slug=row['slug'])
                    for row in reader]
                Category.objects.bulk_create(categories_to_create)
                print('Данные для Category загружены')

    def import_title(self):
        """Импортирует данные для модели Title."""
        if Title.objects.exists():
            print('Данные для Title уже загружены')
        else:
            with open(BASE_DIR / 'static/data/titles.csv',
                      encoding='utf8') as file:
                reader = DictReader(file)
                titles_to_create = []
                for row in reader:
                    category_id = row.pop('category')
                    category = Category.objects.get(id=category_id)
                    title = Title(category=category, **row)
                    titles_to_create.append(title)
                Title.objects.bulk_create(titles_to_create)
                print('Данные для Title загружены')

    def import_genre_title(self):
        """Импортирует данные для модели GenreTitle."""
        if GenreTitle.objects.exists():
            print('Данные для GenreTitle уже загружены')
        else:
            with open(BASE_DIR / 'static/data/genre_title.csv',
                      encoding='utf8') as file:
                reader = DictReader(file)
                genre_titles_to_create = [
                    GenreTitle(id=row['id'], title_id=row['title_id'],
                               genre_id=row['genre_id']) for row in reader]
                GenreTitle.objects.bulk_create(genre_titles_to_create)
                print('Данные для GenreTitle загружены')

    def import_review(self):
        """Импортирует данные для модели Review."""
        if Review.objects.exists():
            print('Данные для Review уже загружены')
        else:
            with open(BASE_DIR / 'static/data/review.csv',
                      encoding='utf8') as file:
                reader = DictReader(file)
                reviews_to_create = []
                for row in reader:
                    author_id = row.pop('author')
                    author = User.objects.get(id=author_id)
                    review = Review(author=author, **row)
                    reviews_to_create.append(review)
                Review.objects.bulk_create(reviews_to_create)
                print('Данные для Review загружены')

    def import_comments(self):
        """Импортирует данные для модели Comment."""
        if Comments.objects.exists():
            print('Данные для Comment уже загружены')
        else:
            with open(BASE_DIR / 'static/data/comments.csv',
                      encoding='utf8') as file:
                reader = DictReader(file)
                comments_to_create = []
                for row in reader:
                    author_id = row.pop('author')
                    author = User.objects.get(id=author_id)
                    comment = Comments(author=author, **row)
                    comments_to_create.append(comment)
                Comments.objects.bulk_create(comments_to_create)
                print('Данные для Comment загружены')

    def handle(self, *args, **kwargs):
        """Обработка команды."""
        self.import_user()
        self.import_genre()
        self.import_category()
        self.import_title()
        self.import_genre_title()
        self.import_review()
        self.import_comments()
