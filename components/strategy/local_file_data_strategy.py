import json
import os

from components.strategy.data_strategy import DataStrategy


class LocalFileDataStrategy(DataStrategy):
    DATA_DIR = os.path.join(os.environ["HOME"], ".kintai_paccho")
    DATA_JSON = os.path.join(DATA_DIR, "employee_data.json")

    def read(self) -> dict:
        if not os.path.exists(self.DATA_JSON):
            self.write({})
        f = open(self.DATA_JSON, "r")
        json_str = f.read()
        f.close()
        return json.loads(json_str)

    def write(self, data):
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR, exist_ok=True)
        f = open(self.DATA_JSON, "w")
        f.write(json.dumps(data))
        f.close()
