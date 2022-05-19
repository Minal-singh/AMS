import django_filters
from .models import Student


class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = Student
        fields = ["first_name", "last_name", "email"]
