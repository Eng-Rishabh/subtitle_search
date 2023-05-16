from pynamodb.models import Model
from myserver.settings import DB_TABLE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from pynamodb.attributes import UnicodeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

WRITE_CAPACITY_UNIT = 10
READ_CAPACITY_UNIT = 5


class Text(Model):
    class Meta:
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        region = 'ap-south-1'
        table_name = DB_TABLE

    content = UnicodeAttribute(hash_key=True)
    start_time = UnicodeAttribute(range_key=True)
    end_time = UnicodeAttribute()
    video_url = UnicodeAttribute()

    # optional way to do without using the opensearch saving each non-stop words in the model and timestamp where
    # they occur Define the Global Secondary Index then searchin on the word by word is enables which timestamp has
    # greater no occurrence will be most relevant but per word query can be more than aws free tier read and write
    # allotted rate so assignment requirement may not satisfy for the latency of 1 second.

    # class SearchByWordIndex(GlobalSecondaryIndex):
    #     class Meta:
    #         projection = AllProjection()
    #         index_name = 'SearchByWord'
    #
    #     word = UnicodeAttribute(hash_key=True)
    #     text_id = UnicodeAttribute(range_key=True)

    # Attach the index to the model
    # search_by_word_index = SearchByWordIndex()


if not Text.exists():
    Text.create_table(read_capacity_units=READ_CAPACITY_UNIT, write_capacity_units=WRITE_CAPACITY_UNIT, wait=True, billing_mode='PROVISIONED')
