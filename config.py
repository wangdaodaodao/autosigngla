#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def load_cookie():
    """加载 cookie 配置"""
    try:
        with open('cookie.json', 'r') as f:
            data = json.load(f)
            return data.get('glados', {}).get('cookie', '')
    except Exception as e:
        print(f"读取 cookie 失败: {e}")
        return ''

# GLaDOS配置
GLADOS_CONFIG = {
    "cookie": load_cookie()
}

# WxPusher配置
PUSH_CONFIG = {
    "wx_pusher": {
        "enable": True,
        "token": "AT_DA1IXmogP80uJiZlFtU4ZhAmVvQdUJK4",
        "uid": "UID_ikc0HQoKmCw9ln88ZmRZSQOguR15"
    }
}

# 服务器配置
SERVER_CONFIG = {
    "host": "panel15.serv00.com",
    "env": "production",
    "deploy_path": "/home/onwoywnooy/glados_checkin",
    "timezone": "Asia/Shanghai"
}

# 定时任务配置
SCHEDULE_CONFIG = {
    "checkin_time_start": "14:25",
    "checkin_time_end": "14:25",
    "retry_times": 3,
    "retry_interval": 300
}

# Server酱推送配置
PUSH_CONFIG = {
    "server_chan": {
        "send_key": "SCT265538T8vcj9P3kpTRStO1wDWmyy0Xh",
        "enable": False,  # 禁用Server酱
    },
    
    # WxPusher配置
    "wx_pusher": {
        "enable": True,
        "token": "AT_DA1IXmogP80uJiZlFtU4ZhAmVvQdUJK4",
        "uid": "UID_ikc0HQoKmCw9ln88ZmRZSQOguR15"
    },
    
    # 推送策略
    "push_on_success": True,
    "push_on_failure": True
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",        # 日志级别
    "file": "checkin.log",  # 日志文件名
    "max_size": 10485760,   # 日志文件大小限制，默认10MB
    "backup_count": 5       # 保留的日志文件数量
}

