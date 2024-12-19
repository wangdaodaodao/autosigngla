#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from wx_push import WxPusher
from config import PUSH_CONFIG

# 设置日志
logging.basicConfig(level=logging.INFO)

def test_push():
    try:
        # 初始化推送器
        pusher = WxPusher(PUSH_CONFIG["wx_pusher"]["token"])
        
        # 测试消息
        test_message = """
📢 测试推送
━━━━━━━━━━
这是一条测试消息
请确认是否收到
━━━━━━━━━━
"""
        
        # 发送测试
        logging.info("开始发送测试推送")
        result = pusher.send("测试通知", test_message)
        logging.info(f"推送结果: {'成功' if result else '失败'}")
        
    except Exception as e:
        logging.error(f"测试推送异常: {e}")

if __name__ == "__main__":
    test_push() 