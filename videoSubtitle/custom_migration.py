import boto3
from myserver.settings import DB_TABLE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
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

import os
import sys
from django.core.management import execute_from_command_line
from videoSubtitle.models import setup_dynamodb


def main():
    # Setup DynamoDB tables and indices

    setup_dynamodb()

    # Run Django management commands
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myserver.settings')
    # execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
