#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLaDOS 配置文件
"""

import json
import logging

def load_cookie():
    """加载 cookie 配置"""
    try:
        with open('cookie.json', 'r') as f:
            data = json.load(f)
            return data.get('glados', {}).get('cookie', '')
    except Exception as e:
        logging.warning(f"读取 cookie 失败: {e}")
        return ''

# GLaDOS配置
GLADOS_CONFIG = {
    "cookie": load_cookie(),  # 从 cookie.json 加载
    "base_url": "https://glados.space"  # GLaDOS 网站地址
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "file": "checkin.log",
    "max_size": 10485760,   # 10MB
    "backup_count": 5
} 