import logging
from datetime import datetime
from traceback import TracebackException

logger = logging.getLogger()

# KingOfTime APIの制限時間帯の定数
KOT_API_RESTRICTED_TIME_RANGES = [
    ("0830", "1000"),  # 朝の制限時間帯
    ("1730", "1830"),  # 夕方の制限時間帯
]

# 共通メッセージ定数
KOT_API_RESTRICTED_TIME_MESSAGE = "[08:30 ～ 10:00, 17:30 ～ 18:30] の時間帯はAPIの都合で{operation}できないんだ。ごめん:paccho:"


def response_configuration_help(say):
    say(
        """
まだ kintai-paccho の設定をしていないみたいだね
"/employee-code 1234" のように入力するぱっちょ！
King of Time にログインしたあとに画面右上の自分の名前の左に出ている数字やアルファベットを入力してね！
    """
    )


def response_kot_error(say, e: Exception):
    msg = "".join(TracebackException.from_exception(e).format())
    logger.error(msg)
    say(f"King of Time からエラーレスポンスが返ってきたぱっちょ！ ```{msg}```")


def response_general_error(say, e: Exception):
    msg = "".join(TracebackException.from_exception(e).format())
    logger.error(msg)
    say(f"エラーが発生したぱっちょ！しばらく待ってからもう一度試してみてね！ ```{msg}```")


def is_kot_api_available():
    """
    KingOfTime APIが現在利用可能かどうかをチェックする

    Returns:
        bool: APIが利用可能な時間帯であればTrue、制限時間帯であればFalse
    """
    time_now_str = datetime.now().strftime("%H%M")

    for start_time, end_time in KOT_API_RESTRICTED_TIME_RANGES:
        if start_time < time_now_str < end_time:
            return False

    return True
