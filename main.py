#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLaDOS Bot 主程序
自动启动所有服务并保持运行
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime
import signal

# 导入各个模块
from tgbot_handler import run_bot
from tgbot_scheduler import run_scheduler

def setup_logging():
    """配置日志"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "main.log")),
            logging.StreamHandler()
        ]
    )

def signal_handler(signum, frame):
    """处理退出信号"""
    logging.info("收到退出信号，正在关闭服务...")
    sys.exit(0)

def run_as_daemon():
    """以守护进程方式运行"""
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as err:
        logging.error(f'fork #1 失败: {err}')
        sys.exit(1)
    
    # 修改工作目录
    os.chdir('/')
    os.umask(0)
    os.setsid()
    
    # 第二次 fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as err:
        logging.error(f'fork #2 失败: {err}')
        sys.exit(1)
    
    # 重定向标准文件描述符
    sys.stdout.flush()
    sys.stderr.flush()
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
    with open('/dev/null', 'a+') as f:
        os.dup2(f.fileno(), sys.stderr.fileno())

def write_pid():
    """写入 PID 文件"""
    pid_file = "bot.pid"
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    logging.info(f"PID {os.getpid()} 已写入 {pid_file}")

def main():
    """主函数"""
    setup_logging()
    logging.info("启动 GLaDOS Bot...")
    
    # 注册信号处理
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # 写入 PID
    write_pid()
    
    try:
        # 创建线程运行 Bot 和定时任务
        bot_thread = threading.Thread(target=run_bot, name="BotThread")
        scheduler_thread = threading.Thread(target=run_scheduler, name="SchedulerThread")
        
        # 设置为守护线程
        bot_thread.daemon = True
        scheduler_thread.daemon = True
        
        # 启动线程
        bot_thread.start()
        scheduler_thread.start()
        
        logging.info("所有服务已启动")
        
        # 等待线程结束
        while True:
            if not bot_thread.is_alive() or not scheduler_thread.is_alive():
                logging.error("服务异常退出，正在重启...")
                if not bot_thread.is_alive():
                    bot_thread = threading.Thread(target=run_bot, name="BotThread")
                    bot_thread.daemon = True
                    bot_thread.start()
                if not scheduler_thread.is_alive():
                    scheduler_thread = threading.Thread(target=run_scheduler, name="SchedulerThread")
                    scheduler_thread.daemon = True
                    scheduler_thread.start()
            time.sleep(60)
            
    except KeyboardInterrupt:
        logging.info("收到中断信号，正在关闭服务...")
    except Exception as e:
        logging.error(f"程序异常: {e}")
    finally:
        # 清理 PID 文件
        if os.path.exists("bot.pid"):
            os.remove("bot.pid")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--daemon':
        run_as_daemon()
    main() 