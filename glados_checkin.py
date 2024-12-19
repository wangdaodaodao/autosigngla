#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import logging
import json
import time
from datetime import datetime, timedelta
from wx_push import WxPusher
from config import GLADOS_CONFIG, PUSH_CONFIG

class GladosCheckin:
    def __init__(self, cookie):
        self.base_url = "https://glados.rocks"
        self.cookie = cookie
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/109.0.0.0",
            "Cookie": self.cookie
        }
        self.session = requests.session()

    def check_cookie_status(self):
        """检查 cookie 状态"""
        try:
            # 从 cookie 中提取过期时间
            cookie_str = self.cookie
            if 'koa:sess=' in cookie_str:
                import base64
                import json
                
                # 提取 koa:sess 的值
                sess = cookie_str.split('koa:sess=')[1].split(';')[0]
                # base64 解码
                try:
                    decoded = base64.b64decode(sess).decode('utf-8')
                    sess_data = json.loads(decoded)
                    
                    # 获取过期时间
                    expire_timestamp = sess_data.get('_expire', 0) / 1000  # 转换为秒
                    now_timestamp = time.time()
                    
                    days_left = (expire_timestamp - now_timestamp) / (24 * 3600)
                    
                    return True, {
                        'status': 'normal' if days_left > 0 else 'expired',
                        'days_left': int(days_left) if days_left > 0 else 0
                    }
                except:
                    return False, {'status': 'invalid', 'days_left': 0}
            return False, {'status': 'invalid', 'days_left': 0}
        except Exception as e:
            logging.error(f"Cookie 检查异常: {e}")
            return False, {'status': 'error', 'days_left': 0}

    def checkin(self):
        try:
            # 获取北京时间
            beijing_time = datetime.now() + timedelta(hours=7)
            logging.info(f"开始签到 - 北京时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 检查 cookie 状态
            cookie_valid, cookie_info = self.check_cookie_status()
            cookie_status = "✅ 正常" if cookie_valid and cookie_info['status'] == 'normal' else "❌ 异常"
            cookie_expire = f"({cookie_info['days_left']}天后过期)" if cookie_valid else "(已过期)"
            
            response = self.session.post(
                f"{self.base_url}/api/user/checkin",
                json={"token": "glados.one"},
                headers=self.headers
            )
            
            logging.info(f"签到响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"签到响应内容: {response.text}")
                
                # 获取账户状态
                status_success, status_data = self.check_status()
                if not status_success:
                    return False, "状态检查失败"
                
                # 处理已签到情况
                if "Checkin Repeats" in result.get('message', ''):
                    logging.info("今日已签到")
                    
                    # 安全获取积分变化
                    points = '0'
                    checkin_list = result.get('list', [])
                    if checkin_list and len(checkin_list) > 0:
                        points = checkin_list[0].get('change', '0')
                    
                    message = f"""
📢 GLaDOS 签到通知
━━━━━━━━━━
📅 时间：{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}
👤 账号：{status_data.get('email', 'unknown')}
⏰ 剩余：{status_data.get('leftDays', 'unknown')}天
✨ 积分：+{points}
🎯 状态：✅ 今日已完成签到
🔐 Cookie：{cookie_status} {cookie_expire}
📝 登录 ssh 后执行以下命令更新 cookie_manager.py
━━━━━━━━━━
🔗 点击消息前往官网
"""
                    # 推送已签到消息
                    if PUSH_CONFIG["wx_pusher"]["enable"]:
                        try:
                            pusher = WxPusher(PUSH_CONFIG["wx_pusher"]["token"])
                            logging.info("发送已签到通知")
                            push_result = pusher.send("GLaDOS 签到通知", message)
                            logging.info(f"推送结果: {'成功' if push_result else '失败'}")
                        except Exception as e:
                            logging.error(f"推送异常: {e}")
                    
                    return True, message
                
                # 处理签到失败情况
                error_msg = f"签到失败: {result.get('message', '未知错误')}"
                logging.error(error_msg)
                return False, error_msg
            
            error_msg = f"请求失败: HTTP {response.status_code}"
            logging.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"签到异常: {e}"
            logging.error(error_msg)
            return False, error_msg

    def check_status(self):
        try:
            response = self.session.get(f"{self.base_url}/api/user/status", headers=self.headers)
            if response.status_code == 200:
                return True, response.json()['data']
            return False, f"状态检查失败: HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def push_message(self, message):
        try:
            if PUSH_CONFIG["wx_pusher"]["enable"]:
                wx_pusher = WxPusher(PUSH_CONFIG["wx_pusher"]["token"])
                return wx_pusher.send("GLaDOS 签到通知", message)
            return True
        except Exception as e:
            logging.error(f"推送失败: {e}")
            return False

def main():
    try:
        import os
        
        # 设置日志
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            filename=os.path.join(log_dir, "checkin.log"),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 初始化对象
        checker = GladosCheckin(GLADOS_CONFIG["cookie"])
        
        # 执行签到
        success, message = checker.checkin()
        
    except Exception as e:
        logging.error(f"程序执行异常: {e}")

if __name__ == "__main__":
    main()