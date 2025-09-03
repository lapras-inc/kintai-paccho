import unittest
from unittest import mock
from unittest.mock import MagicMock

from components.requester import KOTException
from components.typing import SlackRequest
from components.usecase import RecordType
from handler.jp.time_recorder import record_clock_in, record_clock_out, record_end_break, record_start_break


class TestTimeRecorder(unittest.TestCase):
    @mock.patch("handler.jp.time_recorder.response_kot_error")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.timecard_check.get_active_employees")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    @mock.patch("handler.jp.timecard_check.get_daily_schedule_data")
    def test_record_clock_in(self, mocked_get_daily_schedule_data, mocked_get_daily_timacard_data, mocked_get_active_employees, mocked_is_kot_api_available, mocked_get_key, mocked_record_time, mocked_response_kot_error):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        # 勤怠エラーチェック用のモック設定
        mocked_get_active_employees.return_value = []
        mocked_get_daily_timacard_data.return_value = []
        mocked_get_daily_schedule_data.return_value = []

        record_clock_in(say=say, request=request)

        # Employee.get_keyが2回呼ばれる
        self.assertEqual(mocked_get_key.call_count, 2)

        self.assertEqual(mocked_record_time.call_count, 1)

        mocked_record_time_call_args, _ = mocked_record_time.call_args
        self.assertEqual(mocked_record_time_call_args[0], RecordType.CLOCK_IN)
        self.assertEqual(mocked_record_time_call_args[1], "dummy-employee-key")

        self.assertEqual(mocked_response_kot_error.call_count, 0)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("おはー", say_call_args[0])

    @mock.patch("components.repo.Employee.get_key", return_value="key-0009")
    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.timecard_check.get_active_employees")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    @mock.patch("handler.jp.timecard_check.get_daily_schedule_data")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("handler.jp.time_recorder.response_kot_error")
    def test_record_clock_in__with_timecard_error(
        self, mocked_response_kot_error, mocked_record_time, mocked_get_daily_schedule_data,
        mocked_get_daily_timacard_data, mocked_get_active_employees, mocked_is_kot_api_available, 
        mocked_get_key
    ):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        # アクティブな従業員のモック
        mocked_get_active_employees.return_value = [
            {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
        ]

        # 勤怠データのモック（実際のAPIレスポンス形式）
        mocked_get_daily_timacard_data.return_value = [
            {
                "date": "2025-08-30",
                "dailyWorkings": [
                    {
                        "isError": True,
                        "employeeKey": "key-0009",
                        "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
                    },
                ],
            },
        ]

        # スケジュールデータのモック（実際のAPIレスポンス形式）
        mocked_get_daily_schedule_data.return_value = [
            {
                "date": "2025-08-30",
                "dailySchedules": [
                    {
                        "employeeKey": "key-0009",
                        "scheduleTypeName": "通常勤務",
                        "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
                    },
                ],
            },
        ]

        record_clock_in(say=say, request=request)

        # Employee.get_keyが2回呼ばれる（record_clock_in + check_timecard_errors_for_user）
        self.assertEqual(mocked_get_key.call_count, 2)

        self.assertEqual(mocked_record_time.call_count, 1)

        mocked_record_time_call_args, _ = mocked_record_time.call_args
        self.assertEqual(mocked_record_time_call_args[0], RecordType.CLOCK_IN)
        self.assertEqual(mocked_record_time_call_args[1], "key-0009")

        # エラーメッセージが送信されることを確認
        self.assertEqual(say.call_count, 2)
        say_call_args, _ = say.call_args_list[0]
        self.assertIn("おはー", say_call_args[0])
        say_call_args, _ = say.call_args_list[1]
        self.assertIn("勤怠エラーがあるみたい！早めに修正しようね！", say_call_args[0])

        self.assertEqual(mocked_response_kot_error.call_count, 0)

    @mock.patch("components.repo.Employee.get_key", return_value="key-0009")
    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.timecard_check.get_active_employees")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    @mock.patch("handler.jp.timecard_check.get_daily_schedule_data")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("handler.jp.time_recorder.response_kot_error")
    def test_record_clock_in__without_timecard_error(
        self, mocked_response_kot_error, mocked_record_time, mocked_get_daily_schedule_data,
        mocked_get_daily_timacard_data, mocked_get_active_employees, mocked_is_kot_api_available, 
        mocked_get_key
    ):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        # アクティブな従業員のモック
        mocked_get_active_employees.return_value = [
            {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
        ]

        # エラーなしの勤怠データ
        mocked_get_daily_timacard_data.return_value = [
            {
                "date": "2025-08-30",
                "dailyWorkings": [
                    {
                        "isError": False,
                        "employeeKey": "key-0009",
                        "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
                    },
                ],
            },
        ]

        # スケジュールデータ
        mocked_get_daily_schedule_data.return_value = [
            {
                "date": "2025-08-30",
                "dailySchedules": [
                    {
                        "employeeKey": "key-0009",
                        "scheduleTypeName": "通常勤務",
                        "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
                    },
                ],
            },
        ]

        record_clock_in(say=say, request=request)

        # Employee.get_keyが2回呼ばれる
        self.assertEqual(mocked_get_key.call_count, 2)

        self.assertEqual(mocked_record_time.call_count, 1)

        mocked_record_time_call_args, _ = mocked_record_time.call_args
        self.assertEqual(mocked_record_time_call_args[0], RecordType.CLOCK_IN)
        self.assertEqual(mocked_record_time_call_args[1], "key-0009")

        # エラーメッセージが送信されないことを確認（おはーメッセージのみ）
        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("おはー", say_call_args[0])

        self.assertEqual(mocked_response_kot_error.call_count, 0)

    @mock.patch("handler.jp.time_recorder.response_kot_error")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("components.repo.Employee.get_key", return_value=None)
    def test_record_clock_in__employee_not_found(self, mocked_get_key, mocked_record_time, mocked_response_kot_error):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_clock_in(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 0)

        self.assertEqual(mocked_response_kot_error.call_count, 0)

    @mock.patch("handler.jp.time_recorder.record_time", side_effect=KOTException)
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_clock_in__error(self, mocked_get_key, mocked_record_time):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_clock_in(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("エラーレスポンスが返ってきた", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.record_time", side_effect=Exception)
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_clock_in__general_error(self, mocked_get_key, mocked_record_time):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_clock_in(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("しばらく待ってからもう一度試して", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.response_kot_error")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_clock_out(self, mocked_get_key, mocked_record_time, mocked_response_kot_error):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_clock_out(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        mocked_record_time_call_args, _ = mocked_record_time.call_args
        self.assertEqual(mocked_record_time_call_args[0], RecordType.CLOCK_OUT)
        self.assertEqual(mocked_record_time_call_args[1], "dummy-employee-key")

        self.assertEqual(mocked_response_kot_error.call_count, 0)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("おつー", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.response_kot_error")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("components.repo.Employee.get_key", return_value=None)
    def test_record_clock_out__employee_not_found(self, mocked_get_key, mocked_record_time, mocked_response_kot_error):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_clock_out(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 0)

        self.assertEqual(mocked_response_kot_error.call_count, 0)

    @mock.patch("handler.jp.time_recorder.record_time", side_effect=KOTException)
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_clock_out__error(self, mocked_get_key, mocked_record_time):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_clock_out(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("エラーレスポンスが返ってきた", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.record_time", side_effect=Exception)
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_clock_out__general_error(self, mocked_get_key, mocked_record_time):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_clock_out(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("しばらく待ってからもう一度試して", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.response_kot_error")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_start_break(self, mocked_get_key, mocked_record_time, mocked_response_kot_error):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_start_break(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        mocked_record_time_call_args, _ = mocked_record_time.call_args
        self.assertEqual(mocked_record_time_call_args[0], RecordType.START_BREAK)
        self.assertEqual(mocked_record_time_call_args[1], "dummy-employee-key")

        self.assertEqual(mocked_response_kot_error.call_count, 0)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("ゆっくり休んでね", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.response_kot_error")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("components.repo.Employee.get_key", return_value=None)
    def test_record_start_break__employee_not_found(
        self, mocked_get_key, mocked_record_time, mocked_response_kot_error
    ):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_start_break(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 0)

        self.assertEqual(mocked_response_kot_error.call_count, 0)

    @mock.patch("handler.jp.time_recorder.record_time", side_effect=KOTException)
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_start_break__error(self, mocked_get_key, mocked_record_time):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_start_break(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("エラーレスポンスが返ってきた", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.record_time", side_effect=Exception)
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_start_break__general_error(self, mocked_get_key, mocked_record_time):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_start_break(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("しばらく待ってからもう一度試して", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.response_kot_error")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_end_break(self, mocked_get_key, mocked_record_time, mocked_response_kot_error):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_end_break(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        mocked_record_time_call_args, _ = mocked_record_time.call_args
        self.assertEqual(mocked_record_time_call_args[0], RecordType.END_BREAK)
        self.assertEqual(mocked_record_time_call_args[1], "dummy-employee-key")

        self.assertEqual(mocked_response_kot_error.call_count, 0)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("がんばっていこ", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.response_kot_error")
    @mock.patch("handler.jp.time_recorder.record_time")
    @mock.patch("components.repo.Employee.get_key", return_value=None)
    def test_record_end_break__employee_not_found(self, mocked_get_key, mocked_record_time, mocked_response_kot_error):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_end_break(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 0)

        self.assertEqual(mocked_response_kot_error.call_count, 0)

    @mock.patch("handler.jp.time_recorder.record_time", side_effect=KOTException)
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_end_break__error(self, mocked_get_key, mocked_record_time):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_end_break(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("エラーレスポンスが返ってきた", say_call_args[0])

    @mock.patch("handler.jp.time_recorder.record_time", side_effect=Exception)
    @mock.patch("components.repo.Employee.get_key", return_value="dummy-employee-key")
    def test_record_end_break__general_error(self, mocked_get_key, mocked_record_time):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        record_end_break(say=say, request=request)

        self.assertEqual(mocked_get_key.call_count, 1)

        self.assertEqual(mocked_record_time.call_count, 1)

        self.assertEqual(say.call_count, 1)
        say_call_args, _ = say.call_args
        self.assertIn("しばらく待ってからもう一度試して", say_call_args[0])
