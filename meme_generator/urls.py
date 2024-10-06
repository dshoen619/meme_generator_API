# urls.py
from django.urls import path
from .views import (UserSignupView, 
                    UserLoginView, 
                    UserLogoutView, 
                    RetrieveMemeView, 
                    MemeView,
                    CreateMemeTemplateView,
                    ReceiveAllTemplatesView,
                    RateMemeView,
                    RandomMemeView,
                    TopRatedMemesView
                    )

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/',UserLogoutView.as_view(), name='logout'),
    path('api/memes/<int:meme_id>/', RetrieveMemeView.as_view(), name='retrieve_meme'),
    path('api/memes/', MemeView.as_view(), name = 'meme_request'),
    path('api/meme_template/create/', CreateMemeTemplateView.as_view(), name = 'create_meme_template'),
    path('api/templates/', ReceiveAllTemplatesView.as_view(), name = 'receive_all_templates'),
    path('api/memes/<int:meme_id>/rate/', RateMemeView.as_view(), name='rate_meme'),
    path('api/memes/random/', RandomMemeView.as_view(), name='random_meme'),
    path('api/memes/top/', TopRatedMemesView.as_view(), name='top memes')
]


