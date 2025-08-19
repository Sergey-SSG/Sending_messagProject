from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import ProfileUpdateView, RegisterView, UserBlockView, UserListView

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="mailing:home"), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/block/<int:pk>/", UserBlockView.as_view(), name="block_user"),
]
