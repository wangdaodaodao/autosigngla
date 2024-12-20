#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import logging
import json
import time
from datetime import datetime, timedelta
from tgbot_sender import TelegramPusher
from glados_config import GLADOS_CONFIG, LOG_CONFIG
from tgbot_config import TELEGRAM_CONFIG

class GladosCheckin:
    def __init__(self, cookie):
        self.base_url = GLADOS_CONFIG["base_url"]
        self.cookie = cookie
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
            
            # 设置请求头，指定编码
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/109.0.0.0",
                "Cookie": self.cookie,
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/user/checkin",
                json={"token": "glados.one"},
                headers=headers
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
                    
                    # Telegram消息模板
                    message = f"""
🤖 *GLaDOS Bot 签到报告*
━━━━━━━━━━
⏰ 时间：`{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}`
📧 账号：`{status_data.get('email', 'unknown')}`
⌛️ 剩余：`{status_data.get('leftDays', 'unknown')}天`
💎 积分：`+{points}`
✅ 状态：今日已完成签到
🔑 Cookie：{cookie_status} {cookie_expire}
━━━━━━━━━━
[点击访问官网](https://glados.rocks)
"""
                    
                    # 推送到 Telegram
                    self.push_message(message)
                    
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
        """检查账户状态"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/109.0.0.0",
                "Cookie": self.cookie,
                "Accept": "application/json"
            }
            response = self.session.get(
                f"{self.base_url}/api/user/status",
                headers=headers
            )
            if response.status_code == 200:
                return True, response.json()['data']
            return False, f"状态检查失败: HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def push_message(self, message):
        """
        推送消息到 Telegram
        """
        try:
            if TELEGRAM_CONFIG["enable"]:
                tg_pusher = TelegramPusher(
                    TELEGRAM_CONFIG["bot_token"],
                    TELEGRAM_CONFIG["chat_id"]
                )
                result = tg_pusher.send(TELEGRAM_CONFIG["message_template"]["title"], message)
                logging.info(f"Telegram推送{'成功' if result else '失败'}")
                return result
            return True
            
        except Exception as e:
            logging.error(f"Telegram推送异常: {e}")
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
        
        # 添加控制台输出
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        
        # 检查是否为测试模
        import sys
        is_test = "--test" in sys.argv
        
        # 检查配置
        logging.info("正在检查配置...")
        logging.info(f"Cookie 长度: {len(GLADOS_CONFIG['cookie'])}")
        logging.info(f"Telegram Bot Token: {TELEGRAM_CONFIG['bot_token'][:10]}...")
        logging.info(f"Telegram Chat ID: {TELEGRAM_CONFIG['chat_id']}")
        
        if is_test:
            # 测试模式：只发送测试消息
            logging.info("运行测试模式")
            test_message = f"""
🧪 *GLaDOS Bot 测试运行*
━━━━━━━━━━
⏰ 时间：`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
📋 测试项目：
• 配置检查 ✓
• 日志系统 ✓
• 消息推送 ⏳

🤖 *Bot 信息*
• Token: `{TELEGRAM_CONFIG['bot_token']}`
• Chat ID: `{TELEGRAM_CONFIG['chat_id']}`
━━━━━━━━━━
这是一条测试消息，如果你看到这条消息，说明 Bot 运行正常！
"""
            # 初始化对象并发送测试消息
            checker = GladosCheckin(GLADOS_CONFIG["cookie"])
            checker.push_message(test_message)
            logging.info("测试消息已发送")
            return
        
        # 正常模式：执行签到
        checker = GladosCheckin(GLADOS_CONFIG["cookie"])
        success, message = checker.checkin()
        
    except Exception as e:
        logging.error(f"程序执行异常: {e}")

if __name__ == "__main__":
    main() 