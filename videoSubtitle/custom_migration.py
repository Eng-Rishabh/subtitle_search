import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from myserver.settings import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID
# from videoSubtitle.models import READ_CAPACITY_UNIT, WRITE_CAPACITY_UNIT, Subtitle


# def create_table(dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb',
#                                   aws_access_key_id=AWS_ACCESS_KEY_ID,
#                                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#                                   region_name='ap-south-1'
#                                   )
#
#     table = dynamodb.create_table(
#         TableName=DB_TABLE,
#         KeySchema=[
#             {
#                 'AttributeName': 'content',
#                 'KeyType': 'HASH'
#             }
#         ],
#         AttributeDefinitions=[
#             {
#                 'AttributeName': 'content',
#                 'AttributeType': 'S'
#             },
#
#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': READ_CAPACITY_UNIT,
#             'WriteCapacityUnits': WRITE_CAPACITY_UNIT
#         }
#     )
#     return table
#
#
# if __name__ == '__main__':
#     # my_table = create_table()
#     # my_table.meta.client.get_waiter('table_exists').wait(TableName=DB_TABLE)
#     # print("Table status:", my_table.table_status)
#
#     if not Subtitle.Table.table_exists():
#         Subtitle.create_table(wait=True)
#     # print(my_table.item_count)


def start_indexing():
    host = 'search-dynamodb-opensearch-url-my-ej7z72akx4etoq57qoq353t47i.ap-south-1.es.amazonaws.com'
    region = 'ap-south-1'

    service = 'es'
    awsauth = AWS4Auth(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region, service)

    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    mapping = {
        'mappings': {
            'properties': {
                'content': {
                    'type': 'text'
                },
                'start_time': {
                    'type': 'keyword'
                },
                'end_time': {
                    'type': 'keyword'
                },
                'video_url': {
                    'type': 'keyword'
                }
            }
        }
    }

    index_name = 'subtitles'
    client.indices.create(index=index_name, body=mapping)

    # for testing
    # document = {
    #     "content": 'The subtitle content',
    #     "start_time": '10:00:00',
    #     "end_time": '10:10:00',
    #     "video_url": 'https://www.example.com/video.mp4'
    # }
    #
    # client.index(index=index_name, body=document)
    #
    # search_query = 'subtitle'
    # query = {
    #     'query': {
    #         'match': {
    #             'content': search_query
    #         }
    #     }
    # }
    #
    # response = client.search(index=index_name, body=query)


def main():
    # Setup DynamoDB tables and indices
    pass
    # setup_dynamodb()


if __name__ == '__main__':
    main()
