from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from .views import GetUserView, LogoutView, RegisterView, WelcomeView, LoginView, UserProfileView, RegisterFormView
from booth.views import BoothView
from visualizer.views import VisualizerView

urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),
    path('', WelcomeView.as_view(), name='welcome'),
    path("signin/", LoginView.as_view(), name="signin"),
    path("profile/", UserProfileView.as_view(), name='user_profile'),
    path('registerUser/', RegisterFormView.as_view(), name='registerUser'),
    path('booth/<int:voting_id>/', BoothView.as_view(), name='booth'),
    path('visualizer/<int:voting_id>/', VisualizerView.as_view(), name='visualizer'),
]
