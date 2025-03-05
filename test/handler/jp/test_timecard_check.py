import unittest
from unittest import mock
from unittest.mock import MagicMock

from components.requester import KOTException
from components.typing import SlackRequest
from handler.jp.timecard_check import announce_timecard_errors


class TestTimecardCheck(unittest.TestCase):
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    def test_announce_timecard_errors__success_with_errors(self, mocked_get_daily_timacard_data):
        # 勤怠エラーがある場合のモックデータを準備
        mocked_get_daily_timacard_data.return_value = [
            {
                "date": "2023-04-01",
                "dailyWorkings": [
                    {"isError": True, "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"}},
                    {"isError": True, "currentDateEmployee": {"code": "0010", "lastName": "熊本", "firstName": "太郎"}},
                ],
            },
            {
                "date": "2023-04-02",
                "dailyWorkings": [
                    {"isError": True, "currentDateEmployee": {"code": "0100", "lastName": "らぷ", "firstName": "らす"}},
                    {
                        # 唯一勤怠エラーではない
                        "isError": False,
                        "currentDateEmployee": {"code": "0200", "lastName": "テスト", "firstName": "ユーザー"},
                    },
                ],
            },
        ]

        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(say.call_count, 1)

        say_call_args, _ = say.call_args
        message = say_call_args[0]

        # 基本的なメッセージ内容の確認
        self.assertIn("勤怠エラーがある人をお知らせするよ", message)
        self.assertIn("■2023-04-01", message)
        self.assertIn("0009 山田 伝蔵", message)
        self.assertIn("0010 熊本 太郎", message)
        self.assertIn("■2023-04-02", message)
        self.assertIn("0100 らぷ らす", message)

        # エラーがない人は表示されていないことを確認
        self.assertNotIn("0200 テスト ユーザー", message)

    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    def test_announce_timecard_errors__success_no_errors(self, mocked_get_daily_timacard_data):
        # 勤怠エラーがない場合のモックデータを準備
        mocked_get_daily_timacard_data.return_value = [
            {
                "date": "2023-04-01",
                "dailyWorkings": [
                    {"isError": False, "currentDateEmployee": {"code": "0009", "lastName": "山田", "firstName": "伝蔵"}}
                ],
            }
        ]

        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(say.call_count, 1)

        say_call_args, _ = say.call_args
        message = say_call_args[0]

        # エラーがない場合のメッセージ内容の確認
        self.assertIn("勤怠エラーの人はいないよ！やったね！", message)

    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data")
    def test_announce_timecard_errors__no_data(self, mocked_get_daily_timacard_data):
        # データが空の場合
        mocked_get_daily_timacard_data.return_value = []

        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(say.call_count, 1)

        say_call_args, _ = say.call_args
        message = say_call_args[0]

        # データがない場合のメッセージ内容の確認
        self.assertIn("勤怠データが見つからなかったよ", message)

    @mock.patch("handler.jp.timecard_check.response_kot_error")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data", side_effect=KOTException)
    def test_announce_timecard_errors__kot_error(self, mocked_get_daily_timacard_data, mocked_response_kot_error):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(mocked_response_kot_error.call_count, 1)

    @mock.patch("handler.jp.timecard_check.response_general_error")
    @mock.patch("handler.jp.timecard_check.get_daily_timacard_data", side_effect=Exception)
    def test_announce_timecard_errors__general_error(
        self, mocked_get_daily_timacard_data, mocked_response_general_error
    ):
        say = MagicMock()
        request = SlackRequest(channel_id="dummy-channel-id", user_id="dummy-user-id", text="dummy-text")

        announce_timecard_errors(say=say, request=request)

        self.assertEqual(mocked_get_daily_timacard_data.call_count, 1)
        self.assertEqual(mocked_response_general_error.call_count, 1)
