from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path
from .views import RegisterView, ProfileUpdateView

app_name = "users"

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='mailing:home'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
]
