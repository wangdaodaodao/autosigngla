#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import logging
import time
import json
from tgbot_config import TELEGRAM_CONFIG

class TelegramPusher:
    """
    Telegram 消息推送类
    使用方法:
    pusher = TelegramPusher(bot_token, chat_id)
    pusher.send("消息标题", "消息内容")
    """
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = TELEGRAM_CONFIG["api"]["base_url"].format(token=bot_token) + "/sendMessage"
        self.timeout = TELEGRAM_CONFIG["api"]["timeout"]
        self.retry_times = TELEGRAM_CONFIG["api"]["retry_times"]
        self.retry_delay = TELEGRAM_CONFIG["api"]["retry_delay"]

    def send(self, title, content):
        """
        发送消息到 Telegram
        :param title: 消息标题
        :param content: 消息内容
        :return: bool 发送结果
        """
        try:
            message = f"*{title}*\n\n{content}"
            logging.debug(f"准备发送消息: {message}")
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": TELEGRAM_CONFIG["message_template"]["parse_mode"],
                "disable_web_page_preview": TELEGRAM_CONFIG["message_template"]["disable_web_page_preview"],
                "disable_notification": TELEGRAM_CONFIG["message_template"]["disable_notification"]
            }
            logging.debug(f"请求数据: {json.dumps(payload, ensure_ascii=False)}")
            
            # 发送请求
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logging.info("Telegram 消息推送成功")
                return True
            else:
                logging.error(f"Telegram 消息推送失败: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Telegram 消息推送异常: {e}")
            return False 