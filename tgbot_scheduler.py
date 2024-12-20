#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Bot 定时任务管理器
"""

import schedule
import time
import logging
import random
from datetime import datetime, timedelta
from tgbot_sender import TelegramPusher
from tgbot_config import TELEGRAM_CONFIG, SCHEDULER_CONFIG
from glados_notify import GladosCheckin
from glados_config import GLADOS_CONFIG

def get_random_time(base_time):
    """获取随机时间（前后30分钟范围内）"""
    base = datetime.strptime(base_time, "%H:%M")
    delta = random.randint(-30, 30)
    random_time = base + timedelta(minutes=delta)
    return random_time.strftime("%H:%M")

def send_daily_reminder():
    """发送每日提醒"""
    try:
        now = datetime.now()
        # 周末检查
        if not SCHEDULER_CONFIG["enable_weekend"] and now.weekday() >= 5:
            logging.info("周末不执行任务")
            return

        message = f"""
📅 *每日提醒*
━━━━━━━━━━
⏰ 时间：`{now.strftime('%Y-%m-%d %H:%M:%S')}`
📌 待办事项：
• GLaDOS 签到
• 流量查询
• 账号状态检查

🔔 Tips: 
• 可以回复 /checkin 立即执行签到
• 使用 /help 查看所有命令
━━━━━━━━━━
"""
        pusher = TelegramPusher(
            TELEGRAM_CONFIG["bot_token"],
            TELEGRAM_CONFIG["chat_id"]
        )
        result = pusher.send("每日提醒", message)
        if result:
            logging.info("发送每日提醒成功")
        else:
            logging.error("发送每日提醒失败")
    except Exception as e:
        logging.error(f"发送每日提醒异常: {e}")

def do_checkin():
    """执行签到任务"""
    try:
        now = datetime.now()
        # 周末检查
        if not SCHEDULER_CONFIG["enable_weekend"] and now.weekday() >= 5:
            logging.info("周末不执行签到")
            return

        checker = GladosCheckin(GLADOS_CONFIG["cookie"])
        success, message = checker.checkin()
        
        if not success and SCHEDULER_CONFIG["retry_interval"] > 0:
            logging.info(f"{SCHEDULER_CONFIG['retry_interval']}秒后重试签到")
            time.sleep(SCHEDULER_CONFIG["retry_interval"])
            success, message = checker.checkin()
        
        logging.info(f"签到{'成功' if success else '失败'}")
    except Exception as e:
        logging.error(f"签到任务异常: {e}")

def run_scheduler():
    """运行定时任务"""
    logging.info("启动定时任务...")
    
    # 获取随机执行时间
    reminder_time = get_random_time(SCHEDULER_CONFIG["reminder_time"])
    checkin_time = get_random_time(SCHEDULER_CONFIG["checkin_time"])
    
    logging.info(f"提醒时间: {reminder_time}")
    logging.info(f"签到时间: {checkin_time}")
    
    # 设置定时任务
    schedule.every().day.at(reminder_time).do(send_daily_reminder)
    schedule.every().day.at(checkin_time).do(do_checkin)
    
    logging.info("定时任务已启动")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logging.error(f"定时任务异常: {e}")
            time.sleep(SCHEDULER_CONFIG["retry_interval"])

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    run_scheduler() 