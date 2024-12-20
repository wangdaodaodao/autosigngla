#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Bot 命令处理器
"""

import logging
import telegram
from telegram.ext import Updater, CommandHandler
from tgbot_config import TELEGRAM_CONFIG, PROXY_CONFIG
from glados_notify import GladosCheckin
from glados_config import GLADOS_CONFIG
from telegram.utils.request import Request

def start(update, context):
    """处理 /start 命令"""
    message = """
👋 *欢迎使用 GLaDOS Bot*
━━━━━━━━━━
支持的命令：
• /start - 显示此帮助信息
• /checkin - 立即执行签到
• /status - 查询账号状态
• /usage - 查询流量使用情况
• /help - 显示帮助信息
━━━━━━━━━━
"""
    update.message.reply_text(message, parse_mode='Markdown')

def checkin(update, context):
    """处理 /checkin 命令"""
    update.message.reply_text("正在执行签到...", parse_mode='Markdown')
    checker = GladosCheckin(GLADOS_CONFIG["cookie"])
    success, message = checker.checkin()
    update.message.reply_text(message, parse_mode='Markdown')

def status(update, context):
    """���理 /status 命令"""
    checker = GladosCheckin(GLADOS_CONFIG["cookie"])
    success, data = checker.check_status()
    if success:
        message = f"""
📊 *账号状态*
━━━━━━━━━━
📧 邮箱：`{data.get('email', 'unknown')}`
⌛️ 剩余天数：`{data.get('leftDays', 'unknown')}天`
💎 积分：`{data.get('points', 'unknown')}`
━━━━━━━━━━
"""
    else:
        message = "❌ 获取状态失败"
    
    update.message.reply_text(message, parse_mode='Markdown')

def usage(update, context):
    """处理 /usage 命令"""
    checker = GladosCheckin(GLADOS_CONFIG["cookie"])
    success, data = checker.check_status()
    if success:
        message = f"""
📈 *流量使用情况*
━━━━━━━━━━
🔄 已用：`{data.get('traffic', 'unknown')}`
📊 总量：`{data.get('trafficTotal', 'unknown')}`
⚡️ 重置日期：`{data.get('resetDay', 'unknown')}`
━━━━━━━━━━
"""
    else:
        message = "❌ 获取流量信息失败"
    
    update.message.reply_text(message, parse_mode='Markdown')

def help_command(update, context):
    """处理 /help 命令"""
    message = """
ℹ️ *GLaDOS Bot 使用帮助*
━━━━━━━━━━
🔹 基本命令：
• /start - 开始使用
• /checkin - 执行签到
• /status - 查看状态
• /usage - 流量查询
• /help - 显示此帮助

🔸 使用说明：
1. 每天会自动执行签到
2. 可以随时手动签到
3. 支持查询账号状态
4. 可以查看流量使用情况

🔔 提示：
• 签到失败会自动重试
• 可以设置静音推送
━━━━━━━━━━
"""
    update.message.reply_text(message, parse_mode='Markdown')

def run_bot():
    """运行 Bot"""
    # 配置请求
    request = Request(
        connect_timeout=30.0,
        read_timeout=30.0,
        con_pool_size=16  # 增加连接池大小
    )

    bot = telegram.Bot(
        token=TELEGRAM_CONFIG["bot_token"],
        request=request
    )

    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher

    # 注册命令处理器
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("checkin", checkin))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("usage", usage))
    dp.add_handler(CommandHandler("help", help_command))

    # 启动 Bot
    updater.start_polling()
    logging.info("Bot 已启动")
    updater.idle()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    run_bot() 