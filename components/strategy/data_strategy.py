import os


class DataStrategy:
    def read(self) -> dict:
        raise NotImplementedError()

    def write(self, data):
        raise NotImplementedError()


def create_data_strategy() -> DataStrategy:
    if os.environ.get("DATA_STRATEGY") == "DynamoDBDataStrategy":
        from components.strategy.dynamodb_data_strategy import DynamoDBDataStrategy

        return DynamoDBDataStrategy()
    else:
        from components.strategy.local_file_data_strategy import LocalFileDataStrategy

        return LocalFileDataStrategy()
