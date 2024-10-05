# urls.py
from django.urls import path
from .views import UserSignupView, UserLoginView, UserLogoutView, RetrieveMemeView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/',UserLogoutView.as_view(), name='logout'),
    path('api/memes/<int:meme_id>/', RetrieveMemeView.as_view(), name='retrieve_meme')
]

