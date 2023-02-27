#this will setup the urls for our path.
from django.urls import path
from social_app import views
urlpatterns = [
    # moment the user enter the home url it takes to the index page.
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like_post', views.like_post, name='like_post'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path ('follow', views.follow, name = 'follow'),
    path('search', views.search, name='search'),
    path('self_profile', views.self_profile, name= 'self_profile'),
    # delete the product.
    path('delete-product/<str:pk>', views.deleteProduct, name="delete-prod")
]

