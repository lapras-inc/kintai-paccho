import json
import os
import pathlib
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta

from components.repo import Employee
from components.requester import KOTException
from components.typing import SlackRequest
from components.usecase import get_active_employees, get_daily_schedule_data, get_daily_timacard_data

from .helper import (
    KOT_API_RESTRICTED_TIME_MESSAGE,
    is_kot_api_available,
    response_configuration_help,
    response_general_error,
    response_kot_error,
)


def announce_timecard_errors(say, request: SlackRequest):
    """
    先月1日 ~ 前日までに勤怠エラーがある人をアナウンスする
    """

    try:
        # APIの利用制限時間帯のチェック
        if not is_kot_api_available():
            say(KOT_API_RESTRICTED_TIME_MESSAGE.format(operation="勤怠関連の操作"))
            return

        # ----------------------------------------
        # 日付範囲の構築をし、勤怠情報を取得
        # 取得範囲は「先月1日から前日まで」
        # ----------------------------------------

        today = datetime.now().date()
        # 先月の1日 ~ 前日の日付文字列を構築
        first_day_of_last_month = today.replace(day=1) - relativedelta(months=1)
        yesterday = today - timedelta(days=1)

        first_day_of_last_month_str = first_day_of_last_month.strftime("%Y-%m-%d")
        yesterday_str = yesterday.strftime("%Y-%m-%d")

        # 勤怠データ、スケジュールデータを取得
        print(f"date range: {first_day_of_last_month_str} to {yesterday_str}")
        timecard_data = get_daily_timacard_data(from_date=first_day_of_last_month_str, to_date=yesterday_str)
        schedule_data = get_daily_schedule_data(from_date=first_day_of_last_month_str, to_date=yesterday_str)

        # データが空の場合のチェック
        if len(timecard_data) == 0:
            say(":den_paccho1: < 勤怠データが見つからなかったよ！")
            return

        if len(schedule_data) == 0:
            say(":den_paccho1: < スケジュールデータが見つからなかったよ！")
            return

        # ----------------------------------------
        # 勤怠データから勤怠エラーの人を抽出
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

        # ----------------------------------------
        # スケジュールデータから勤怠情報なしの人を抽出
        # ----------------------------------------

        # 退職タイミングによって退職者の勤務予定が中途半端に作成されているため、退職者の勤務予定を除外する必要がある
        active_employees = get_active_employees()
        active_employee_codes = {emp["code"] for emp in active_employees}

        # スケジュールで「通常勤務」の人と日付のマッピングを作成
        scheduled_normal_work = {}
        for daily_schedule in schedule_data:
            schedule_date = daily_schedule.get("date", "")
            daily_schedules = daily_schedule.get("dailySchedules", [])

            for schedule in daily_schedules:
                # 従業員番号比較で退職者のデータは除外
                if schedule.get("currentDateEmployee", {}).get("code") not in active_employee_codes:
                    continue

                # 通常勤務のスケジュールのみ対象
                if schedule.get("scheduleTypeName") == "通常勤務":
                    employee = schedule.get("currentDateEmployee", {})
                    employee_key = schedule.get("employeeKey", "")

                    if schedule_date not in scheduled_normal_work:
                        scheduled_normal_work[schedule_date] = []

                    scheduled_normal_work[schedule_date].append(
                        {"employeeKey": employee_key, "currentDateEmployee": employee}
                    )

        # 勤怠データから勤怠記録がある社員のキーを日付ごとに抽出
        timecard_recorded = {}
        for daily_data in timecard_data:
            timecard_date = daily_data.get("date", "")
            daily_workings = daily_data.get("dailyWorkings", [])

            if timecard_date not in timecard_recorded:
                timecard_recorded[timecard_date] = set()

            for working in daily_workings:
                employee_key = working.get("employeeKey", "")
                timecard_recorded[timecard_date].add(employee_key)

        # スケジュールでは「通常勤務」だが勤怠記録がない社員を抽出
        for day, employees in scheduled_normal_work.items():
            # その日の勤怠記録がある社員のセット
            recorded_employees = timecard_recorded.get(day, set())
            missing_timecard = []

            for employee_data in employees:
                employee_key = employee_data.get("employeeKey", "")
                # 勤怠記録がない場合
                if employee_key not in recorded_employees:
                    # エラー情報として追加
                    employee_info = employee_data.get("currentDateEmployee", {})
                    missing_timecard.append(
                        {
                            "employeeKey": employee_key,
                            "currentDateEmployee": employee_info,
                            "isError": True,  # 勤怠記録なしもエラー扱い
                        }
                    )

            # エラーデータに追加
            if missing_timecard:
                if day in error_data:
                    error_data[day].extend(missing_timecard)
                else:
                    error_data[day] = missing_timecard

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
