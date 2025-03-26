import unittest
from unittest import mock
from unittest.mock import MagicMock

from components.requester import KOTException
from components.typing import SlackRequest
from handler.jp.timecard_check import announce_timecard_errors


class TestTimecardCheck(unittest.TestCase):
    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.timecard_check.get_active_employees")
    @mock.patch("handler.jp.timecard_check.get_daily_schedule_data")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    def test_announce_timecard_errors__success_with_errors(
        self,
        mocked_get_daily_timacard_data,
        mocked_get_daily_schedule_data,
        mocked_get_active_employees,
        mocked_is_kot_api_available,
    ):
        # 勤怠エラーがある場合のモックデータを準備
        mocked_get_daily_timacard_data.return_value = [
            {
                "date": "2023-04-01",
                "dailyWorkings": [
                    {
                        "isError": True,
                        "employeeKey": "key-0009",
                        "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
                    },
                    {
                        "isError": True,
                        "employeeKey": "key-0010",
                        "currentDateEmployee": {"code": "0010", "lastName": "熊本", "firstName": "太郎"},
                    },
                ],
            },
            {
                "date": "2023-04-02",
                "dailyWorkings": [
                    {
                        "isError": True,
                        "employeeKey": "key-0100",
                        "currentDateEmployee": {"code": "0100", "lastName": "らぷ", "firstName": "らす"},
                    },
                    {
                        # 唯一勤怠エラーではない
                        "isError": False,
                        "employeeKey": "key-0200",
                        "currentDateEmployee": {"code": "0200", "lastName": "テスト", "firstName": "ユーザー"},
                    },
                ],
            },
        ]

        # スケジュールデータのモック
        mocked_get_daily_schedule_data.return_value = [
            {
                "date": "2023-04-01",
                "dailySchedules": [
                    {
                        "scheduleTypeName": "通常勤務",
                        "employeeKey": "key-0009",
                        "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
                    },
                    {
                        "scheduleTypeName": "通常勤務",
                        "employeeKey": "key-0010",
                        "currentDateEmployee": {"code": "0010", "lastName": "熊本", "firstName": "太郎"},
                    },
                    {
                        "scheduleTypeName": "通常勤務",
                        "employeeKey": "key-0011",
                        "currentDateEmployee": {"code": "0011", "lastName": "大阪", "firstName": "花子"},
                    },
                ],
            },
            {
                "date": "2023-04-02",
                "dailySchedules": [
                    {
                        "scheduleTypeName": "通常勤務",
                        "employeeKey": "key-0100",
                        "currentDateEmployee": {"code": "0100", "lastName": "らぷ", "firstName": "らす"},
                    },
                    {
                        "scheduleTypeName": "通常勤務",
                        "employeeKey": "key-0200",
                        "currentDateEmployee": {"code": "0200", "lastName": "テスト", "firstName": "ユーザー"},
                    },
                ],
            },
        ]

        # アクティブな従業員のモック
        mocked_get_active_employees.return_value = [
            {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
            {"code": "0010", "lastName": "熊本", "firstName": "太郎"},
            {"code": "0011", "lastName": "大阪", "firstName": "花子"},
            {"code": "0100", "lastName": "らぷ", "firstName": "らす"},
            {"code": "0200", "lastName": "テスト", "firstName": "ユーザー"},
        ]

        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(mocked_get_daily_schedule_data.call_count, 1)
        self.assertEqual(mocked_get_active_employees.call_count, 1)
        self.assertEqual(say.call_count, 1)

        say_call_args, _ = say.call_args
        message = say_call_args[0]

        # 基本的なメッセージ内容の確認
        self.assertIn("勤怠エラーがある人をお知らせするよ", message)
        self.assertIn("■2023-04-01", message)
        self.assertIn("0009 山田 伝蔵", message)
        self.assertIn("0010 熊本 太郎", message)
        self.assertIn("0011 大阪 花子", message)  # スケジュールはあるが勤怠記録がない
        self.assertIn("■2023-04-02", message)
        self.assertIn("0100 らぷ らす", message)

        # エラーがない人は表示されていないことを確認
        self.assertNotIn("0200 テスト ユーザー", message)

    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.timecard_check.get_active_employees")
    @mock.patch("handler.jp.timecard_check.get_daily_schedule_data")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    def test_announce_timecard_errors__success_no_errors(
        self,
        mocked_get_daily_timacard_data,
        mocked_get_daily_schedule_data,
        mocked_get_active_employees,
        mocked_is_kot_api_available,
    ):
        # 勤怠エラーがない場合のモックデータを準備
        mocked_get_daily_timacard_data.return_value = [
            {
                "date": "2023-04-01",
                "dailyWorkings": [
                    {
                        "isError": False,
                        "employeeKey": "key-0009",
                        "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
                    }
                ],
            }
        ]

        # スケジュールデータのモック
        mocked_get_daily_schedule_data.return_value = [
            {
                "date": "2023-04-01",
                "dailySchedules": [
                    {
                        "scheduleTypeName": "通常勤務",
                        "employeeKey": "key-0009",
                        "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
                    },
                ],
            }
        ]

        # アクティブな従業員のモック
        mocked_get_active_employees.return_value = [
            {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
        ]

        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(mocked_get_daily_schedule_data.call_count, 1)
        self.assertEqual(mocked_get_active_employees.call_count, 1)
        self.assertEqual(say.call_count, 1)

        say_call_args, _ = say.call_args
        message = say_call_args[0]

        # エラーがない場合のメッセージ内容の確認
        self.assertIn("勤怠エラーの人はいないよ！やったね！", message)

    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.timecard_check.get_active_employees", return_value=[])
    @mock.patch("handler.jp.timecard_check.get_daily_schedule_data", return_value=[])
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    def test_announce_timecard_errors__no_timecard_data(
        self,
        mocked_get_daily_timacard_data,
        mocked_get_daily_schedule_data,
        mocked_get_active_employees,
        mocked_is_kot_api_available,
    ):
        # データが空の場合
        mocked_get_daily_timacard_data.return_value = []

        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(mocked_get_daily_schedule_data.call_count, 1)
        self.assertEqual(mocked_get_active_employees.call_count, 0)  # スケジュールデータが空の場合はそこで終了するため従業員情報は取得しない
        self.assertEqual(say.call_count, 1)

        say_call_args, _ = say.call_args
        message = say_call_args[0]

        # データがない場合のメッセージ内容の確認
        self.assertIn("勤怠データが見つからなかったよ", message)

    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.timecard_check.get_active_employees", return_value=[])
    @mock.patch("handler.jp.timecard_check.get_daily_schedule_data")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    def test_announce_timecard_errors__no_schedule_data(
        self,
        mocked_get_daily_timacard_data,
        mocked_get_daily_schedule_data,
        mocked_get_active_employees,
        mocked_is_kot_api_available,
    ):
        # タイムカードデータあり、スケジュールデータなし
        mocked_get_daily_timacard_data.return_value = [
            {
                "date": "2023-04-01",
                "dailyWorkings": [
                    {
                        "isError": False,
                        "employeeKey": "key-0009",
                        "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"},
                    }
                ],
            }
        ]
        mocked_get_daily_schedule_data.return_value = []

        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(mocked_get_daily_schedule_data.call_count, 1)
        self.assertEqual(mocked_get_active_employees.call_count, 0)  # スケジュールデータがない場合はアクティブな従業員情報は取得しない
        self.assertEqual(say.call_count, 1)

        say_call_args, _ = say.call_args
        message = say_call_args[0]

        # スケジュールデータがない場合のメッセージ内容の確認
        self.assertIn("スケジュールデータが見つからなかったよ", message)

    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=False)
    def test_announce_timecard_errors__api_not_available(self, mocked_is_kot_api_available):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_is_kot_api_available.call_count, 1)
        self.assertEqual(say.call_count, 1)

        say_call_args, _ = say.call_args
        message = say_call_args[0]

        # API制限時間帯のメッセージ内容の確認
        self.assertIn("勤怠関連の操作", message)

    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.timecard_check.response_kot_error")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data", side_effect=KOTException)
    def test_announce_timecard_errors__kot_error(
        self, mocked_get_daily_timacard_data, mocked_response_kot_error, mocked_is_kot_api_available
    ):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(mocked_response_kot_error.call_count, 1)

    @mock.patch("handler.jp.timecard_check.is_kot_api_available", return_value=True)
    @mock.patch("handler.jp.timecard_check.response_general_error")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data", side_effect=Exception)
    def test_announce_timecard_errors__general_error(
        self, mocked_get_daily_timacard_data, mocked_response_general_error, mocked_is_kot_api_available
    ):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(mocked_response_general_error.call_count, 1)
