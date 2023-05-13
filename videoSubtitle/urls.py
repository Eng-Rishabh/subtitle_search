from django.urls import path
from .views import Home, VideoUpload, SearchSubtitle

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('upload/', VideoUpload.as_view(), name='video_upload_form'),
    path('search/', SearchSubtitle.as_view(), name='search_subtitles_form'),
]
