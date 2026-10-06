from django.urls import path

from . import views

urlpatterns = [path("avaliar/<str:data>/", views.avaliar, name="avaliar")]
