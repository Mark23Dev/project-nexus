from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


# Register a new user
class RegisterView(generics.CreateAPIView):
    """
    Register a new user.
    POST /api/v1/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# List all users (admin only)
class UserListView(generics.ListAPIView):
    """
    List all users (admin only).
    GET /api/v1/users/
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# Retrieve or update a user (owner or admin)
class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a user (owner or admin).
    GET /api/v1/users/<id>/
    PATCH /api/v1/users/<id>/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]


#current user's profile view
class MeView(generics.RetrieveAPIView):
    """
    Get the authenticated user's profile.
    GET /api/v1/users/me/
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


#Change Password View
class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password for the authenticated user.
    POST /api/v1/users/change-password/
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
