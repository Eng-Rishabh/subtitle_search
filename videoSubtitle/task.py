from celery import shared_task
from .models import Subtitle
from django.conf import settings
from django.core.files.storage import default_storage

import subprocess
import tempfile
import re

# @shared_task


def save_subtitle_entries(input_file_path, name):

    default_storage.save("video/"+name, open(input_file_path, 'rb'))
    video_url = default_storage.url("video/" + name)  # Replace 'path/to/video.mp4' with the actual file path in S3
    print("video_url:", video_url)

    with tempfile.NamedTemporaryFile(suffix='.srt', mode='w+t') as temp_file:
        output_file_path = temp_file.name

        # Run CCExtractor command
        command = ['/Users/rishabh/Downloads/ccextractor/mac/ccextractor', '-out=srt', '-o', output_file_path, input_file_path]
        subprocess.run(command, capture_output=True, text=True)

        temp_file.seek(0)
        # with open(output_file_path, 'r') as srt:
        text = temp_file.read()
        matches = re.findall(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\d|\Z)", text,
                             flags=re.DOTALL)

        for match in matches:
            line_number = match[0]
            start_time = match[1]
            end_time = match[2]
            subtitle_text = match[3]

            print(f"Line Number: {line_number}")
            print(f"Start Time: {start_time}")
            print(f"End Time: {end_time}")
            print(f"Subtitle Text: {subtitle_text}\n")
            print("line no type print", type(line_number))
            # subtitle = Subtitle(
            #     content=str(subtitle_text),
            #     start_time=str(start_time),
            #     end_time=str(end_time),
            #     video_url=str(video_url)
            # )
        subtitle = Subtitle(
            content='The subtitle content',
            start_time='10:00:00',
            end_time='10:10:00',
            video_url='https://www.example.com/video.mp4'
        )
        subtitle.save()


