#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Bot 配置文件
"""

# Telegram Bot 配置
TELEGRAM_CONFIG = {
    "bot_token": "7818042748:AAFSA6eo7WXFkpyUeNffBa40DN09lkwfNyw",
    "chat_id": "6421422299",
    "enable": True,
    
    # API 配置
    "api": {
        "base_url": "https://api.telegram.org/bot{token}",
        "timeout": 30,
        "retry_times": 5,
        "retry_delay": 2,
        "api_server": "api.telegram.org"
    },
    
    # 消息模板配置
    "message_template": {
        "title": "GLaDOS Bot 签到报告",
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
        "disable_notification": False
    }
}



# 定时任务配置
SCHEDULER_CONFIG = {
    "reminder_time": "09:00",  # 每日提醒时间
    "checkin_time": "10:30",   # 每日签到时间
    "enable_weekend": True,    # 周末是否执行
    "retry_interval": 300      # 失败重试间隔（秒）
} 