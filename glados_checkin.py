#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLaDOS 自动签到模块

实现原理：
1. 通过分析浏览器开发者工具中的网络请求，发现签到流程：
   - 状态检查：GET /api/user/status
   - 签到请求：POST /api/user/checkin
   
2. 关键点：
   - Cookie 验证：需要 koa:sess 和 koa:sess.sig 两个字段
   - koa:sess 是 base64 编码的 JSON 数据
   - Authorization 头用于请求验证
   - 签到 token 固定为 "glados.one"

调试过程：
1. 首先使用 test_site.py 抓取实际的请求数据
2. 分析请求头和响应数据的格式
3. 验证 cookie 的有效性和格式
4. 测试状态检查接口
5. 实现签到功能并处理各种响应情况

注意事项：
1. Cookie 有效期较长，但建议定期更新
2. 签到需要在每天 UTC+8 0点后进行
3. 重复签到会返回上次签到信息
4. 返回的积分数据可用于判断签到是否成功
"""

import requests
import json
import logging
import base64
from datetime import datetime, timedelta
import time
import os
from scheduler import get_next_run_time, wait_until_run_time
from wx_push import WxPusher
from config import GLADOS_CONFIG, PUSH_CONFIG, SERVER_CONFIG, SCHEDULE_CONFIG
from cookie_manager import CookieManager

class GladosCheckin:
    """
    GLaDOS 签到类
    
    主要功能：
    1. 验证 cookie 格式
    2. 检查账号状态
    3. 执行每日签到
    4. 处理签到结果
    """
    
    def __init__(self, cookie_str):
        """
        初始化签到类
        
        Args:
            cookie_str: 包含 koa:sess 和 koa:sess.sig 的 cookie 字符串
            
        实现说明：
        1. 基础 URL 使用 glados.space 域名
        2. 预设通用的请求头
        3. 保存 cookie 以供后续请求使用
        """
        self.base_url = "https://glados.space"
        self.checkin_url = f"{self.base_url}/api/user/checkin"
        self.status_url = f"{self.base_url}/api/user/status"
        self.cookie_str = cookie_str
        
        # 基础请求头（从浏览器请求中提取的通用头信息）
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cookie": cookie_str
        }
    
    def validate_cookie(self):
        """
        验证 cookie 格式是否正确
        
        验证步骤：
        1. 检查必需的 cookie 字段是否存在
        2. 验证 koa:sess 是否为有效的 base64 编码
        3. 解码后验证是否为有效的 JSON 格式
        
        Returns:
            bool: cookie 格式是否有效
        """
        required_fields = ['koa:sess', 'koa:sess.sig']
        cookie_dict = {}
        
        # 解析 cookie 字符串为字典
        for item in self.cookie_str.split(';'):
            item = item.strip()
            if '=' in item:
                name, value = item.split('=', 1)
                cookie_dict[name] = value
        
        # 检查必需字段
        missing = [field for field in required_fields if field not in cookie_dict]
        if missing:
            logging.error(f"缺少必需的Cookie字段: {', '.join(missing)}")
            return False
            
        # 验证 koa:sess 格式（base64 编码的 JSON）
        sess = cookie_dict.get('koa:sess', '')
        try:
            decoded = base64.b64decode(sess + '=' * (-len(sess) % 4))
            json.loads(decoded)  # 尝试解析 JSON
        except Exception as e:
            logging.error(f"koa:sess 格式无效: {str(e)}")
            return False
            
        return True
    
    def check_status(self):
        """
        检查用户账号状态
        
        实现说明：
        1. 发送 GET 请求到状态检查接口
        2. 验证响应状态码和返回数据
        3. 提取有用的账号信息（邮箱和剩余天数）
        
        Returns:
            tuple: (是否成功, 状态数据/错误信息)
        """
        headers = {
            **self.base_headers,
            "Referer": f"{self.base_url}/console/checkin",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        try:
            response = requests.get(
                self.status_url,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    data = result.get('data', {})
                    return True, {
                        'email': data.get('email'),
                        'leftDays': data.get('leftDays')
                    }
            
            return False, response.json()
            
        except Exception as e:
            logging.error(f"检查状态异常: {str(e)}")
            return False, str(e)
    
    def checkin(self):
        """
        执行签到操作
        
        实现流程：
        1. 验证 cookie 格式
        2. 检查账号状态
        3. 发送签到请求
        4. 处理签到结果
        
        签到结果处理：
        1. 成功签到：返回获得的积分
        2. 重复签到：返回上次签到信息
        3. 签到失败：返回错误信息
        
        Returns:
            tuple: (是否成功, 格式化的消息)
        """
        # 先验证cookie
        if not self.validate_cookie():
            return False, "Cookie 验证失败"
            
        # 检查状态
        status_ok, status_data = self.check_status()
        if not status_ok:
            return False, f"状态检查失败: {status_data}"
        
        # 获取北京时间
        beijing_time = datetime.now() + timedelta(hours=7)  # CET 转北京时间
        
        # 签到请求头（从实际请求中复制的关键头信息）
        headers = {
            **self.base_headers,
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": "2835864063149731976414591193354-900-1440",
            "Origin": self.base_url,
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Priority": "u=3, i"
        }
        
        # 签到数据（固定的 token 值）
        data = {
            "token": "glados.one"
        }
        
        try:
            response = requests.post(
                self.checkin_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            result = response.json()
            
            # 处理不同的签到结果
            if result.get('code') == 0:
                # 签到成功
                points = result.get('points', 0)
                message = f"""
📢 GLaDOS 签到通知
━━━━━━━━━━
📅 时间：{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}
👤 账号：{status_data.get('email', 'unknown')}
⏰ 剩余：{status_data.get('leftDays', 'unknown')}天
✨ 积分：+{points}
🎯 状态：✅ 签到成功
━━━━━━━━━━
🔗 点击消息前往官网
"""
                return True, message
            elif result.get('code') == 1 and "Checkin Repeats" in result.get('message', ''):
                # 今日已签到
                checkin_list = result.get('list', [])
                last_checkin = checkin_list[0] if checkin_list else {}
                points = last_checkin.get('change', '0')
                
                message = f"""
📢 GLaDOS 签到通知
━━━━━━━━━━
📅 时间：{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}
👤 账号：{status_data.get('email', 'unknown')}
⏰ 剩余：{status_data.get('leftDays', 'unknown')}天
✨ 积分：+{points}
🎯 状态：ℹ️ 今日已签到
━━━━━━━━━━
🔗 点击消息前往官网
"""
                return True, message
            else:
                # 签到失败
                message = f"""
📢 GLaDOS 签到通知
━━━━━━━━━━
📅 时间：{beijing_time.strftime('%Y-%m-%d %H:%M:%S')}
👤 账号：{status_data.get('email', 'unknown')}
⏰ 剩余：{status_data.get('leftDays', 'unknown')}天
❌ 错误：{result.get('message', '未知错误')}
🎯 状态：签到失败
━━━━━━━━━━
🔗 点击消息前往官网
"""
                return False, message
                
        except Exception as e:
            logging.error(f"签到异常: {str(e)}")
            return False, f"签到异常: {str(e)}" 

    def check_cookie_validity(self):
        """
        检查 cookie 是否有效
        """
        try:
            # 尝试调用状态接口
            status_ok, _ = self.check_status()
            if not status_ok:
                logging.warning("Cookie 已失效，需要更新")
                return False
            return True
        except Exception as e:
            logging.error(f"检查 cookie 有效性出错: {e}")
            return False

def main():
    try:
        import os
        from config import GLADOS_CONFIG, PUSH_CONFIG
        
        # 设置日志
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            filename=os.path.join(log_dir, "checkin.log"),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        logging.info("开始执行签到任务")
        
        # 初始化对象
        checker = GladosCheckin(GLADOS_CONFIG["cookie"])
        wx_pusher = WxPusher(PUSH_CONFIG["wx_pusher"]["token"])
        
        # 执行签到
        success, message = checker.checkin()
        logging.info(f"签到结果: {'成功' if success else '失败'}")
        
        # 推送结果
        if PUSH_CONFIG["wx_pusher"]["enable"]:
            push_result = wx_pusher.send("GLaDOS 签到通知", message)
            logging.info(f"推送结果: {'成功' if push_result else '失败'}")
            
    except Exception as e:
        error_msg = f"签到异常: {str(e)}"
        logging.error(error_msg)
        if PUSH_CONFIG["wx_pusher"]["enable"]:
            wx_pusher.send("GLaDOS 签到异常", error_msg)

if __name__ == "__main__":
    main() 