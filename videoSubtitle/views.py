from django.shortcuts import render, redirect
from django.views import View
from .task import save_subtitle_entries, search


class Home(View):
    def get(self, request):
        return render(request, "index.html")


class VideoUpload(View):
    def get(self, request):
        return render(request, 'video.html')

    def post(self, request):
        uploaded_file = request.FILES['video']
        with open(f'temp_upload/{uploaded_file.name}', 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        save_subtitle_entries.delay(f"temp_upload/{uploaded_file.name}", uploaded_file.name)
        return redirect('search_subtitles_form')


class SearchSubtitle(View):
    def get(self, request):
        keywords = request.GET.get('keywords', '')  # Retrieve the value of 'keywords' parameter
        search_results = []
        print(keywords)

        if keywords:
            search_results = []
            hits = search(keywords)
            for hit in hits:
                source = hit['_source']
                renamed_source = {
                    'content': source['content'],
                    'start_time': source['start_time'],
                    'end_time': source['end_time'],
                    'video_url': source['video_url']
                }
                search_results.append(renamed_source)

        context = {
            'keywords': keywords,
            'search_results': search_results,
        }

        return render(request, 'subtitle.html', context)
