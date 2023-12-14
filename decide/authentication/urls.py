from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LogoutView, RegisterView, WelcomeView, LoginView, UserProfileView


urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),
    path('', WelcomeView.as_view(), name='welcome'),
    path("signin/", LoginView.as_view(), name="signin"),
    path("profile/", UserProfileView.as_view(), name='user_profile'),
]
