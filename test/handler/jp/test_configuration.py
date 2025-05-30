import unittest
from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock

from freezegun import freeze_time

from components.requester import KOTException
from components.typing import SlackRequest
from handler.jp.configuration import register_employee_code
from handler.jp.helper import is_kot_api_available


class TestConfiguration(unittest.TestCase):
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    @freeze_time("2012-03-21 12:34:56")
    @mock.patch("handler.jp.configuration.register_user")
    def test_register_employee_code(self, mocked_register_user):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        last_name = "dummy-last-name"
        first_name = "dummy-first-name"

        mocked_register_user.return_value = {"last_name": last_name, "first_name": first_name}

        register_employee_code(say=say, request=request)

        self.assertEqual(say.call_count, 1)

        call_args, _ = say.call_args

        self.assertIn(f"{last_name} {first_name}さんの設定が完了", call_args[0])

        self.assertEqual(mocked_register_user.call_count, 1)

    @freeze_time("2025-09-01 08:45:00")
    @mock.patch("handler.jp.configuration.is_kot_api_available", return_value=False)
    @mock.patch("components.usecase.register_user")
    def test_register_employee_code__cant_register(self, mocked_register_user, mocked_is_kot_api_available):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        register_employee_code(say=say, request=request)

        self.assertEqual(say.call_count, 1)

        call_args, _ = say.call_args

        self.assertIn("勤怠登録", call_args[0])

        self.assertFalse(mocked_register_user.called)

    @freeze_time("2012-03-21 12:34:56")
    @mock.patch("handler.jp.configuration.is_kot_api_available", return_value=True)
    @mock.patch("components.usecase.register_user")
    def test_register_employee_code__unset_employee_code(self, mocked_register_user, mocked_is_kot_api_available):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text=None)

        register_employee_code(say=say, request=request)

        self.assertEqual(say.call_count, 2)

        call_args_list = say.call_args_list

        self.assertIn("読み取れなかったよ", call_args_list[0][0][0])
        self.assertIn("/employee-code", call_args_list[1][0][0])

        self.assertFalse(mocked_register_user.called)

    @freeze_time("2012-03-21 12:34:56")
    @mock.patch("handler.jp.configuration.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.configuration.register_user")
    def test_register_employee_code__kot_error(self, mocked_register_user, mocked_is_kot_api_available):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        error_message = "認証に失敗しました"

        mocked_register_user.side_effect = KOTException(error_message)

        register_employee_code(say=say, request=request)

        self.assertEqual(say.call_count, 1)
        call_args_list = say.call_args_list

        self.assertIn("King of Time からエラーレスポンス", call_args_list[0][0][0])
        self.assertIn(error_message, call_args_list[0][0][0])
