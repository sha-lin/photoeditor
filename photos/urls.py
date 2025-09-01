from django.urls import path
from . import views

urlpatterns = [
    path('', views.photo_list, name='photo_list'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('photo/<uuid:photo_id>/', views.photo_detail, name='photo_detail'),
    path('photo/<uuid:photo_id>/status/', views.photo_status, name='photo_status'),
    path('photo/<uuid:photo_id>/download/<str:image_type>/', views.download_image, name='download_image'),
]