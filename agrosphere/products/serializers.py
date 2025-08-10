from rest_framework import serializers
from .models import Product, Category, Review
from django.db.models import Avg


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    vendor = serializers.StringRelatedField(read_only=True)  # vendor email or username display

    class Meta:
        model = Product
        fields = [
            "id",
            "vendor",
            "category",
            "category_id",
            "title",
            "slug",
            "description",
            "price",
            "available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "slug", "created_at", "updated_at", "vendor")

    def create(self, validated_data):
        # vendor set by view from request.user
        category = validated_data.pop("category", None)
        product = Product.objects.create(**validated_data)
        if category:
            product.category = category
            product.save()
        return product

    def update(self, instance, validated_data):
        category = validated_data.pop("category", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if category is not None:
            instance.category = category
        instance.save()
        return instance
    
    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 2) if avg is not None else None

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Show email or username

    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value