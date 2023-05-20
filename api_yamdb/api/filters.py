import django_filters
from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='contains')
    year = django_filters.NumberFilter(field_name='year')
    category = django_filters.AllValuesFilter(field_name='category__slug')
    genre = django_filters.AllValuesFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']
