from components.repo import Employee
from components.requester import KOTException
from components.typing import SlackRequest
from components.usecase import get_daily_timacard_data
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from .helper import response_configuration_help, response_general_error, response_kot_error


def announce_timecard_errors(say, request: SlackRequest):
    """
    先月1日 ~ 前日までに勤怠エラーがある人をアナウンスする
    """

    try:
        # ----------------------------------------
        # 日付範囲の構築をし、勤怠情報を取得
        # 取得範囲は「先月1日から前日まで」
        # ----------------------------------------

        # 先月の1日 ~ 前日の日付文字列を構築
        first_day_of_last_month_str = (date.today() - relativedelta(months=1)).strftime("%Y-%m-%d")
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # 勤怠データを取得
        print(f"date range: {first_day_of_last_month_str} to {yesterday_str}")
        timecard_data = get_daily_timacard_data(from_date=first_day_of_last_month_str, to_date=yesterday_str)
        print(f"data count: {len(timecard_data)}")

        # データが空の場合のチェック
        if len(timecard_data) == 0:
            say(":den_paccho1: < 勤怠データが見つからなかったよ！")
            return

        # ----------------------------------------
        # 勤怠データから通知内容を構築
        # ----------------------------------------

        # 日付ごとのエラーデータ格納用
        # 勤怠エラーがある人のデータを日付ごとに格納する
        # { "2025-02-01": { "code": "0009", "lastName": "山田", "firstName": 伝蔵", "isError": True ....} }
        error_data = {}

        for daily_data in timecard_data:
            error_timecard = []
            for daily_working in daily_data["dailyWorkings"]:
                if daily_working["isError"] == True:
                    error_timecard.append(daily_working)

            if error_timecard:
                timecard_date = daily_data.get("date", "不明")
                error_data[timecard_date] = error_timecard

        if not error_data:
            say(":den_paccho1: < 勤怠エラーの人はいないよ！やったね！")
            return

        # ----------------------------------------
        # 通知メッセージ構築 & 送信
        # ----------------------------------------
        # メッセージの表示サンプル:
        # :den_paccho1: < 勤怠エラーがある人をお知らせするよ！
        #
        # ■2023-04-01
        # 0009 山田 伝蔵
        # 0010 熊本 太郎
        #
        # ■2023-04-02
        # 0100 らぷ らす
        message = ":den_paccho1: < 勤怠エラーがある人をお知らせするよ！\n\n"

        # 日付順でエラーを表示
        for day in sorted(error_data.keys()):
            message += f"■{day}\n"
            # 従業員番号順でエラー対象者を表示する
            sorted_workings = sorted(error_data[day], key=lambda w: w.get("currentDateEmployee", {}).get("code", "不明"))
            for working in sorted_workings:
                employee = working.get("currentDateEmployee", {})
                code = employee.get("code", "不明")
                last_name = employee.get("lastName", "")
                first_name = employee.get("firstName", "")
                message += f"{code} {last_name} {first_name}\n"
            message += "\n"

        say(message)

    except KOTException as e:
        response_kot_error(say, e)
    except Exception as e:
        response_general_error(say, e)
