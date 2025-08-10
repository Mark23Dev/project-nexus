from rest_framework import generics, permissions, filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from rest_framework.response import Response
from django.db.models import Count, Avg

from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer
from .filters import ProductFilter


class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET: List products with filtering, searching, ordering, and caching.
    POST: Create a new product.
    """

    queryset = Product.objects.filter(available=True).select_related("category", "vendor")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["title", "description", "category__name"]
    ordering_fields = ["price", "created_at", "title"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)
        cache.delete("product_list")

    def list(self, request, *args, **kwargs):
        cache_key = "product_list"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 300)  # cache serialized data for 5 minutes
        return response

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve product details.
    PUT/PATCH: Update product.
    DELETE: Delete product.
    """

    queryset = Product.objects.filter(available=True).select_related("category", "vendor")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save()
        cache.delete("product_list")

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete("product_list")

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    List reviews (optionally filtered by product) and create new reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        product_id = self.request.query_params.get("product")
        queryset = Review.objects.all()
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset.select_related("user", "product")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a review.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow users to access their own reviews or implement a permission class for this
        return Review.objects.filter(user=self.request.user).select_related("user", "product")
    
class ProductFacetsView(generics.GenericAPIView):
    """
    Returns facet counts for categories, price ranges, average rating buckets.
    """

    def get(self, request, *args, **kwargs):
        available_products = Product.objects.filter(available=True)

        categories = (
            available_products
            .values("category__name", "category__slug")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        price_buckets = {
            "0-50": available_products.filter(price__gte=0, price__lte=50).count(),
            "51-100": available_products.filter(price__gt=50, price__lte=100).count(),
            "101-500": available_products.filter(price__gt=100, price__lte=500).count(),
            "500+": available_products.filter(price__gt=500).count(),
        }

        rating_buckets = {}
        for rating in range(1, 6):
            count = available_products.annotate(avg_rating=Avg("reviews__rating")).filter(avg_rating__gte=rating).count()
            rating_buckets[f"{rating}_stars_and_up"] = count

        return Response({
            "categories": list(categories),
            "price_ranges": price_buckets,
            "ratings": rating_buckets,
        })