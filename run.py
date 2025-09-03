import logging
import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

from components.typing import SlackRequest
from handler.jp.configuration import register_employee_code
from handler.jp.time_recorder import (
    record_clock_in, record_clock_out, record_end_break, record_start_break
)
from handler.jp.timecard_check import announce_timecard_errors


def get_command_name(base_name):
    """環境に応じてコマンド名を生成する"""
    app_mode = os.environ.get("SLACK_APP_MODE", "production")

    valid_modes = ["production", "test"]
    if app_mode not in valid_modes:
        raise ValueError(
            f"SLACK_APP_MODE must be one of {valid_modes}, got: {app_mode}"
        )

    if app_mode == "test":
        return f"/{base_name}-test"
    return f"/{base_name}"


def create_app(is_test=False):
    if is_test:
        client = WebClient(token="xoxb-valid", base_url="http://localhost:8888")
        app = App(client=client, signing_secret="secret")
        # テスト環境では強制的にテスト用コマンド名を使用
        def get_test_command_name(base_name):
            return f"/{base_name}"

    else:
        token = os.environ["SLACK_BOT_TOKEN"]
        app = App(token=token)
        # 本番環境では環境変数に応じてコマンド名を生成
        get_test_command_name = get_command_name

    @app.event("app_mention")
    def handle_app_mention_events(event, say):
        # 勤怠エラーがある人をアナウンスする
        if "勤怠エラー" in event["text"].lower():
            request = SlackRequest(channel_id=event["channel"], user_id=event["user"], text=event["text"])
            announce_timecard_errors(say, request)

    # record timestamp
    @app.message(re.compile("^おはー[！？!?]*$"))
    def record_clock_in_listener(message, say):
        record_clock_in(say, SlackRequest.build_from_message(message))

    @app.command(get_test_command_name("clock-in"))
    def record_clock_in_command(ack, command, say):
        ack()
        record_clock_in(say, SlackRequest.build_from_command(command))

    @app.message(re.compile("^(店じまい|おつー)[！？!?]*$"))
    def record_clock_out_listener(message, say):
        record_clock_out(say, SlackRequest.build_from_message(message))

    @app.command(get_test_command_name("clock-out"))
    def record_clock_out_command(ack, command, say):
        ack()
        record_clock_out(say, SlackRequest.build_from_command(command))

    @app.message(re.compile("^休憩開始$"))
    def record_start_break_listener(message, say):
        record_start_break(say, SlackRequest.build_from_message(message))

    @app.command(get_test_command_name("start-break"))
    def record_start_break_command(ack, command, say):
        ack()
        record_start_break(say, SlackRequest.build_from_command(command))

    @app.message(re.compile("^休憩終了$"))
    def record_end_break_listener(message, say):
        record_end_break(say, SlackRequest.build_from_message(message))

    @app.command(get_test_command_name("end-break"))
    def record_end_break_command(ack, command, say):
        ack()
        record_end_break(say, SlackRequest.build_from_command(command))

    # setting
    @app.command(get_test_command_name("employee-code"))
    def employee_code_command(ack, command, say):
        ack()
        register_employee_code(say, SlackRequest.build_from_command(command))

    return app


# misc
# FIX ME react only @mention
# @app.event("message")
# def handle_message_events(event, say):
#     if re.search(r'感謝|ありがとう|好き|すごい', event['text']):
#         be_shy(say)
#     elif re.search(r'アレクサ|Alexa|alexa', event['text']):
#         i_am_not_alexa(say)
#     elif re.search(r'Hey Siri', event['text']):
#         i_am_not_siri(say)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    logger.info("start slackbot")

    app = create_app()

    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
