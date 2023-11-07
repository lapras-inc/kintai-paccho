import json
import os
from datetime import datetime

from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

from components.strategy.data_strategy import DataStrategy


class DataModel(Model):
    class Meta:
        table_name = os.environ["DYNAMODB_DATA_TABLE_NAME"]
        region = os.environ["DYNAMODB_REGION"]

    key = UnicodeAttribute(hash_key=True)
    value = UnicodeAttribute()
    updated_at = UnicodeAttribute()


class DynamoDBDataStrategy(DataStrategy):
    DATA_KEY = "employee"

    def read(self) -> dict:
        try:
            record = DataModel.get(hash_key=self.DATA_KEY)
            return json.loads(record.value)
        except DataModel.DoesNotExist:
            self.write({})
            return {}

    def write(self, data):
        DataModel(hash_key=self.DATA_KEY, value=json.dumps(data), updated_at=datetime.now().isoformat()).save()
