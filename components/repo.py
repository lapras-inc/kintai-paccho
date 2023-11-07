import json
import os

from components.strategy.data_strategy import create_data_strategy


class Employee:
    @classmethod
    def create(cls, user_id, key):
        user_data = cls._read()
        user_data[user_id] = key  # KOT の従業員の EmployeeKey
        cls._write(user_data)

    @classmethod
    def get_key(cls, user_id):
        data = cls._read()
        if user_id in data:
            return data[user_id]
        return None

    @classmethod
    def _write(cls, data):
        create_data_strategy().write(data)

    @classmethod
    def _read(cls):
        return create_data_strategy().read()
