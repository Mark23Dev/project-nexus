from django_filters import rest_framework as filters
from django.db.models import Avg
from .models import Product

class ProductFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")
    available = filters.BooleanFilter(field_name="available")
    category = filters.CharFilter(field_name="category__slug", lookup_expr="iexact")
    min_rating = filters.NumberFilter(method="filter_min_rating")

    class Meta:
        model = Product
        fields = ["price_min", "price_max", "available", "category"]

    def filter_min_rating(self, queryset, name, value):
        # Filter products with average rating >= value
        return queryset.annotate(avg_rating=Avg("reviews__rating")).filter(avg_rating__gte=value)
