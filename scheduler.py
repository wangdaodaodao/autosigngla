#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
import logging

def get_next_run_time(target_hour=14, target_minute=50):
    """
    获取下一次运行时间
    
    Args:
        target_hour: 目标小时（24小时制）
        target_minute: 目标分钟
    
    Returns:
        datetime: 下一次运行的时间
    """
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # 如果今天的目标时间已过，设置为明天
    if now >= target_time:
        target_time += timedelta(days=1)
    
    return target_time

def wait_until_run_time(target_time):
    """
    等待直到目标时间
    
    Args:
        target_time: datetime 对象，表示目标时间
    """
    now = datetime.now()
    wait_seconds = (target_time - now).total_seconds()
    
    if wait_seconds > 0:
        logging.info(f"等待到 {target_time.strftime('%Y-%m-%d %H:%M:%S')} 执行任务")
        logging.info(f"需要等待 {wait_seconds:.2f} 秒")
        time.sleep(wait_seconds) 