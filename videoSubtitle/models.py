# from dynamorm import DynaModel, ProjectAll
# from marshmallow import fields, EXCLUDE
# from django.conf import settings
# import datetime
from myserver.settings import DB_TABLE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import boto3

READ_CAPACITY_UNIT = 20
WRITE_CAPACITY_UNIT = 10
# Create your models here.


# class Subtitle(DynaModel):
#     class Table:
#         session_kwargs = {
#             "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
#             "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
#             'region_name': 'ap-south-1'
#         }
#
#         name = settings.DB_TABLE
#         hash_key = 'content'
#         read = READ_CAPACITY_UNIT
#         write = WRITE_CAPACITY_UNIT
#         projection = ProjectAll()
#
#     class Schema:
#         content = fields.String()
#         start_time = fields.String()
#         end_time = fields.String()
#         video_url = fields.String()
#
#         year = fields.Number(missing=lambda: datetime.datetime.utcnow().year)

    # class Meta:
    #     unknown = EXCLUDE

    # class MySchema(Schema):
    #     class Meta:
    #         unknown = EXCLUDE


def setup_dynamodb():
    # Create a DynamoDB client
    dynamodb = boto3.resource('dynamodb',
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                            region_name='ap-south-1'
                    )

    # Define the table schema
    table_name = 'Texts'
    key_schema = [
        {'AttributeName': 'text_id', 'KeyType': 'HASH'},
        {'AttributeName': 'word', 'KeyType': 'RANGE'}
    ]
    attribute_definitions = [
        {'AttributeName': 'text_id', 'AttributeType': 'S'},
        {'AttributeName': 'word', 'AttributeType': 'S'}
    ]
    provisioned_throughput = {
        'ReadCapacityUnits': 5,  # Adjust according to your needs
        'WriteCapacityUnits': 5  # Adjust according to your needs
    }

    # Create the DynamoDB table
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        ProvisionedThroughput=provisioned_throughput
    )

    # Create the Global Secondary Index
    index_name = 'SearchByWord'
    index_key_schema = [
        {'AttributeName': 'word', 'KeyType': 'HASH'},
        {'AttributeName': 'text_id', 'KeyType': 'RANGE'}
    ]
    projection = {'ProjectionType': 'ALL'}  # Adjust according to your needs

    # Define the GSI update request
    gsi_update_request = {
        'Create': {
            'IndexName': index_name,
            'KeySchema': index_key_schema,
            'Projection': projection,
            'ProvisionedThroughput': provisioned_throughput
        }
    }

    # Get the current table description to retrieve the latest attribute definitions
    response = dynamodb.describe_table(TableName=table_name)
    current_attribute_definitions = response['Table']['AttributeDefinitions']

    # Update the table to add the Global Secondary Index
    dynamodb.update_table(
        TableName=table_name,
        AttributeDefinitions=current_attribute_definitions,
        GlobalSecondaryIndexUpdates=[gsi_update_request]
    )

