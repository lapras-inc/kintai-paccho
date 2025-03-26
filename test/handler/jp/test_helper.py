import unittest
from datetime import datetime
from unittest.mock import MagicMock

from freezegun import freeze_time

from components.requester import KOTException
from handler.jp.helper import (
    is_kot_api_available,
    response_configuration_help,
    response_general_error,
    response_kot_error,
)


class TestHelper(unittest.TestCase):
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def test_response_configuration_help(self):
        say = MagicMock()

        response_configuration_help(say=say)

        self.assertEqual(say.call_count, 1)

        args, _ = say.call_args

        self.assertIn("kintai-paccho", args[0])
        self.assertIn("/employee-code", args[0])
        self.assertIn("入力するぱっちょ！", args[0])

    def test_response_kot_error(self):
        say = MagicMock()

        error_message = "dummy error message"

        response_kot_error(say=say, e=KOTException(error_message))

        self.assertEqual(say.call_count, 1)

        call_args_list = say.call_args_list

        self.assertIn("返ってきたぱっちょ！", call_args_list[0][0][0])
        self.assertIn(error_message, call_args_list[0][0][0])

    def test_response_general_error(self):
        say = MagicMock()

        error_message = "dummy error message"

        response_general_error(say=say, e=Exception(error_message))

        self.assertEqual(say.call_count, 1)

        call_args_list = say.call_args_list

        self.assertIn("しばらく待って", call_args_list[0][0][0])
        self.assertIn(error_message, call_args_list[0][0][0])

    def test_is_kot_api_available(self):
        patterns = [
            # morning
            (datetime.strptime("2025-08-01 08:30:59", self.DATE_FORMAT), True),
            (datetime.strptime("2025-08-01 08:31:00", self.DATE_FORMAT), False),
            (datetime.strptime("2025-08-01 09:59:59", self.DATE_FORMAT), False),
            (datetime.strptime("2025-08-01 10:00:00", self.DATE_FORMAT), True),
            # afternoon
            (datetime.strptime("2028-12-01 17:30:59", self.DATE_FORMAT), True),
            (datetime.strptime("2028-12-01 17:31:00", self.DATE_FORMAT), False),
            (datetime.strptime("2028-12-01 18:29:59", self.DATE_FORMAT), False),
            (datetime.strptime("2028-12-01 18:30:00", self.DATE_FORMAT), True),
        ]

        for current_time, can_register in patterns:
            with self.subTest(msg=f"current_time={current_time}, can_register={can_register}"):
                with freeze_time(current_time):
                    self.assertEqual(is_kot_api_available(), can_register)
