import logging
from traceback import TracebackException

logger = logging.getLogger()


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
