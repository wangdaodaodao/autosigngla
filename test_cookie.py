#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cookie_manager import CookieManager
from glados_checkin import GladosCheckin
from config import GLADOS_CONFIG
import logging
import json
import base64
from datetime import datetime

def test_cookie():
    """
    测试 cookie 的有效性和管理功能
    """
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n=== GLaDOS Cookie 测试 ===")
    
    # 1. 测试当前配置的 cookie
    current_cookie = GLADOS_CONFIG["cookie"]
    print("\n1. 当前 Cookie 信息：")
    try:
        sess_data = current_cookie.split('koa:sess=')[1].split(';')[0]
        decoded_data = base64.b64decode(sess_data + '=' * (-len(sess_data) % 4))
        cookie_info = json.loads(decoded_data)
        
        expire_time = datetime.fromtimestamp(cookie_info.get('_expire', 0) / 1000)
        print(f"- 过期时间: {expire_time}")
        print(f"- 用户 ID: {cookie_info.get('userId', 'unknown')}")
        print(f"- 最大有效期: {cookie_info.get('_maxAge', 0) / 1000 / 86400:.1f} 天")
    except Exception as e:
        print(f"解析当前 Cookie 失败: {e}")
    
    # 2. 测试 Cookie 保存功能
    print("\n2. 测试 Cookie 保存：")
    cookie_manager = CookieManager()
    try:
        cookie_manager.save_cookie(current_cookie)
        print("- Cookie 保存成功")
    except Exception as e:
        print(f"- Cookie 保存失败: {e}")
    
    # 3. 测试 Cookie 加载功能
    print("\n3. 测试 Cookie 加载：")
    try:
        loaded_cookie = cookie_manager.load_cookie()
        if loaded_cookie == current_cookie:
            print("- Cookie 加载成功且与原始值匹配")
        else:
            print("- Cookie 加载成功但与原始值不匹配")
    except Exception as e:
        print(f"- Cookie 加载失败: {e}")
    
    # 4. 测试 Cookie 有效性
    print("\n4. 测试 Cookie 有效性：")
    checker = GladosCheckin(current_cookie)
    try:
        if checker.check_cookie_validity():
            print("- Cookie 当前有效")
        else:
            print("- Cookie 已失效")
    except Exception as e:
        print(f"- 检查 Cookie 有效性失败: {e}")
    
    # 5. 测试账号状态
    print("\n5. 测试账号状态：")
    try:
        status_ok, status_data = checker.check_status()
        if status_ok:
            print(f"- 账号邮箱: {status_data.get('email', 'unknown')}")
            print(f"- 剩余天数: {status_data.get('leftDays', 'unknown')}")
        else:
            print(f"- 获取状态失败: {status_data}")
    except Exception as e:
        print(f"- 检查账号状态失败: {e}")

if __name__ == "__main__":
    test_cookie() 