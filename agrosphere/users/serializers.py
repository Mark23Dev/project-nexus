from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user representation for read operations."""
    class Meta:
        model = User
        read_only_fields = ("id", "date_joined", "is_staff", "is_superuser", "kyc_verified")
        fields = ("id", "email", "username", "first_name", "last_name", "phone", "is_vendor", "kyc_verified", "date_joined")


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new users.
    Performs password validation and returns user object on creation.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = User
        fields = ("email", "password", "password2", "first_name", "last_name", "phone", "is_vendor")

    def validate_password(self, value):
        # Use Django's password validators
        password_validation.validate_password(value, self.instance)
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.pop("password2"):
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context.get("request").user)
        return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    For updating non-auth fields of the user profile.
    """
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "username")
