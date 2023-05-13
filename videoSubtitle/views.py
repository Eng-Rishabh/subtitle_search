from django.shortcuts import render, redirect
from django.views import View
from django.core.files.uploadedfile import TemporaryUploadedFile

# import boto3

# from django.core.files.base import ContentFile
# from .task import save_subtitle_entries

# from django.http import HttpResponse
from .task import *

# Create your views here.


class Home(View):
    def get(self, request):
        # sleepy.delay(10)
        return render(request, "index.html")


class VideoUpload(View):
    def get(self, request):
        return render(request, 'video.html')

    def post(self, request):
        print(request.POST.get('title'), '')
        print(request.FILES['video'], '')
        uploaded_file = request.FILES['video']

        if isinstance(uploaded_file, TemporaryUploadedFile):
            # Access the temporary file and its properties
            temp_file_path = uploaded_file.temporary_file_path()
            save_subtitle_entries(temp_file_path, uploaded_file.name)
            content_type = uploaded_file.content_type
            size = uploaded_file.size
            print(temp_file_path)
            uploaded_file.file.close()
            uploaded_file.close()

        return redirect('search_subtitles_form')


class SearchSubtitle(View):
    def get(self, request):
        keywords = request.GET.get('keywords', '')  # Retrieve the value of 'keywords' parameter
        search_results = []
        print(keywords)

        if keywords:
            pass
        # Perform the search logic here and populate the search_results list
        # ...

        context = {
            'keywords': keywords,
            'search_results': search_results,
        }

        return render(request, 'subtitle.html', context)
