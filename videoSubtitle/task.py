from celery import shared_task
from .models import Text
from django.conf import settings
from django.core.files.storage import default_storage
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import subprocess
import tempfile
import re
from os import remove

index_name = 'subtitle'


@shared_task
def save_subtitle_entries(input_file_path, name):

    try:
        default_storage.save("video/" + name, open(input_file_path, 'rb'))
        video_url = default_storage.url("video/" + name)  # Replace 'path/to/video.mp4' with the actual file path in S3
        print("video_url:", video_url)

        host = 'search-dynamodb-opensearch-url-my-ej7z72akx4etoq57qoq353t47i.ap-south-1.es.amazonaws.com'
        region = 'ap-south-1'

        service = 'es'
        awsauth = AWS4Auth(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, region, service)

        client = OpenSearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

        with tempfile.NamedTemporaryFile(suffix='.srt', mode='w+t') as temp_file:
            output_file_path = temp_file.name

            # Run CCExtractor command
            command = ['ccextractor', '-out=srt', '-o', output_file_path,
                       input_file_path]
            subprocess.run(command, capture_output=True, text=True)

            temp_file.seek(0)
            text = temp_file.read()
            matches = re.findall(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\d|\Z)", text,
                                 flags=re.DOTALL)

            for match in matches:
                subtitle = Text(
                    content=match[3],
                    start_time=match[1],
                    end_time=match[2],
                    video_url=video_url
                )
                subtitle.save()

                document = {
                    "content": match[3],
                    "start_time": match[1],
                    "end_time": match[2],
                    "video_url": video_url
                }

                client.index(index=index_name, body=document)

                # line_number = match[0]
                # start_time = match[1]
                # end_time = match[2]
                # subtitle_text = match[3]

            # print(f"Line Number: {line_number}")
            # print(f"Start Time: {start_time}")
            # print(f"End Time: {end_time}")
            # print(f"Subtitle Text: {subtitle_text}\n")
            # print("line no type print", type(line_number))

    finally:
        # close_this.file.close()
        # close_this.close()
        remove(input_file_path)


def search(text):
    host = 'search-dynamodb-opensearch-url-my-ej7z72akx4etoq57qoq353t47i.ap-south-1.es.amazonaws.com'
    region = 'ap-south-1'

    service = 'es'
    awsauth = AWS4Auth('AKIAWKL3DKQFFF2MJ2XJ', 'sCJqH2CKQfqXC3r5zxI1sBCMGVi7e5vlRYiuW3ZR', region, service)

    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    query = {
        'query': {
            'match': {
                'content': text
            }
        }
    }

    response = client.search(index=index_name, body=query)
    return response['hits']['hits']
