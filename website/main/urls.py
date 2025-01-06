from django.urls import path
from . import views
from .views import custom_logout_view
from .views import home, update_post

urlpatterns = [
    path('sign-up', views.sign_up, name='sign-up'),
    path('home', views.home, name='home'),
    path('', views.home, name='home'),
    path('create-post', views.create_post, name='create-post'),
    path('logout/', custom_logout_view, name='logout'),
    path('post/<int:pk>/edit/', update_post, name='post_update'),
    path('', views.crib, name='crib')
]
