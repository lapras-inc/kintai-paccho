import json
import random
import shutil
import string
import tempfile
import unittest
from os import path
from unittest import mock
from unittest.mock import patch

from components.repo import Employee
from components.strategy.local_file_data_strategy import LocalFileDataStrategy


def _random_string(n):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


@patch("components.strategy.data_strategy.create_data_strategy", return_value=LocalFileDataStrategy())
class TestEmployee(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.temp_json = path.join(path.join(self.temp_dir, "employee_data.json"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_create(self, _):
        user_id_1 = _random_string(n=10)
        user_id_2 = _random_string(n=10)
        user_key_1 = _random_string(n=20)
        user_key_2 = _random_string(n=20)

        with mock.patch.multiple(
            "components.strategy.local_file_data_strategy.LocalFileDataStrategy",
            DATA_DIR=self.temp_dir,
            DATA_JSON=self.temp_json,
        ):
            Employee.create(user_id=user_id_1, key=user_key_1)

            Employee.create(user_id=user_id_2, key=user_key_2)

            with open(self.temp_json) as f:
                self.assertDictEqual(json.loads(f.read()), {user_id_1: user_key_1, user_id_2: user_key_2})

    def test_get_key(self, _):
        user_id_1 = _random_string(n=10)
        user_key_1 = _random_string(n=20)

        with open(self.temp_json, "w") as f:
            f.write(json.dumps({user_id_1: user_key_1}))

        with mock.patch.multiple(
            "components.strategy.local_file_data_strategy.LocalFileDataStrategy",
            DATA_DIR=self.temp_dir,
            DATA_JSON=self.temp_json,
        ):
            self.assertIsNone(Employee.get_key("none_key"))

            self.assertDictEqual(LocalFileDataStrategy().read(), {user_id_1: user_key_1})

            self.assertEqual(Employee.get_key(user_id_1), user_key_1)
