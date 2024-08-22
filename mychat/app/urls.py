from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('logout/', views.logout_view, name='logout'),
    path('get_answer/', views.get_answer),
]