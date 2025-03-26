import datetime

from components.requester import KOTException
from components.typing import SlackRequest
from components.usecase import register_user
from handler.jp.helper import KOT_API_RESTRICTED_TIME_MESSAGE, is_kot_api_available, response_kot_error


def register_employee_code(say, request: SlackRequest):
    if not is_kot_api_available():
        say(KOT_API_RESTRICTED_TIME_MESSAGE.format(operation="勤怠登録"))
        return

    if not request.text:
        say("従業員コードが読み取れなかったよ")
        say('"/employee-code 1234" のように入力するぱっちょ！')
        return

    try:
        kot_username = register_user(request.user_id, request.text)
        say(
            "{last_name} {first_name}さんの設定が完了したぱっちょ！".format(
                last_name=kot_username["last_name"], first_name=kot_username["first_name"]
            )
        )
    except KOTException as e:
        response_kot_error(say, e)
