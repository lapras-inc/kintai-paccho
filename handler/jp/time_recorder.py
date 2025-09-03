from components.repo import Employee
from components.requester import KOTException
from components.typing import SlackRequest
from components.usecase import RecordType, record_time

from .helper import response_configuration_help, response_general_error, response_kot_error
from .timecard_check import check_timecard_errors_for_user


def record_clock_in(say, request: SlackRequest):
    employee_key = Employee.get_key(request.user_id)
    if not employee_key:
        return response_configuration_help(say)

    try:
        record_time(RecordType.CLOCK_IN, employee_key)
        say(":den_paccho1: < おはー　だこくしたよ〜")

        # 勤怠エラーチェックがある場合は通知
        check_timecard_errors_for_user(request.user_id, say)

    except KOTException as e:
        response_kot_error(say, e)
    except Exception as e:
        response_general_error(say, e)


def record_clock_out(say, request: SlackRequest):
    employee_key = Employee.get_key(request.user_id)
    if not employee_key:
        return response_configuration_help(say)

    try:
        record_time(RecordType.CLOCK_OUT, employee_key)
        say(":gas_paccho_1: < おつー　打刻したよー")

        # 勤怠エラーチェックがある場合は通知
        check_timecard_errors_for_user(request.user_id, say)
    except KOTException as e:
        response_kot_error(say, e)
    except Exception as e:
        response_general_error(say, e)


def record_start_break(say, request: SlackRequest):
    employee_key = Employee.get_key(request.user_id)
    if not employee_key:
        return response_configuration_help(say)

    try:
        record_time(RecordType.START_BREAK, employee_key)
        say(":gas_paccho_1: < はーい　ゆっくり休んでねー")
    except KOTException as e:
        response_kot_error(say, e)
    except Exception as e:
        response_general_error(say, e)


def record_end_break(say, request: SlackRequest):
    employee_key = Employee.get_key(request.user_id)
    if not employee_key:
        return response_configuration_help(say)

    try:
        record_time(RecordType.END_BREAK, employee_key)
        say(":den_paccho1: < おっけー　がんばっていこ〜")
    except KOTException as e:
        response_kot_error(say, e)
    except Exception as e:
        response_general_error(say, e)
