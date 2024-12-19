#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from glados_checkin import GladosCheckin
from wx_push import WxPusher
from config import GLADOS_CONFIG, PUSH_CONFIG
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_checkin():
    """
    测试签到和推送流程
    """
    print("开始测试签到流程...")
    
    # 初始化签到和推送
    checker = GladosCheckin(GLADOS_CONFIG["cookie"])
    wx_pusher = WxPusher(PUSH_CONFIG["wx_pusher"]["token"])
    
    # 执行签到
    success, message = checker.checkin()
    print(f"签到结果: {'成功' if success else '失败'}")
    print(f"签到消息:\n{message}")
    
    # 测试推送
    if PUSH_CONFIG["wx_pusher"]["enable"]:
        print("\n开始测试推送...")
        if (success and PUSH_CONFIG["push_on_success"]) or \
           (not success and PUSH_CONFIG["push_on_failure"]):
            push_result = wx_pusher.send("", message)
            print(f"推送结果: {'成功' if push_result else '失败'}")
    
if __name__ == "__main__":
    test_checkin() 