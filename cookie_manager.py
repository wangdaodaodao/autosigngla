#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import time
import base64
from datetime import datetime, timezone, timedelta
import re

class CookieManager:
    def __init__(self, file_path='cookie.json'):
        self.file_path = file_path
        
    def load_cookies(self):
        """加载 cookie 配置"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"读取 cookie 失败: {e}")
            return {}
    
    def save_cookies(self, cookies):
        """保存 cookie 配置"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(cookies, f, indent=4)
            return True
        except Exception as e:
            print(f"保存 cookie 失败: {e}")
            return False
    
    def extract_cookie_from_curl(self, curl_command):
        """从 curl 命令中提取 cookie"""
        try:
            # 处理多行命令
            curl_command = curl_command.replace('\\\n', ' ')
            
            # 查找包含 Cookie 的行
            for line in curl_command.split("'"):
                if 'Cookie:' in line:
                    cookie_start = line.find('Cookie:') + 7
                    cookie_value = line[cookie_start:].strip()
                    if cookie_value:
                        return cookie_value
            
            return None
        except Exception as e:
            print(f"提取 cookie 失败: {e}")
            return None
    
    def calculate_expiry(self, timestamp_ms):
        """计算过期时间"""
        try:
            # 转换为秒
            timestamp_s = timestamp_ms / 1000
            
            # 创建 UTC 时间
            utc_time = datetime.fromtimestamp(timestamp_s, timezone.utc)
            
            # 转换为北京时间 (UTC+8)
            beijing_time = utc_time.astimezone(timezone(timedelta(hours=8)))
            
            # 计算剩余天数
            now = datetime.now(timezone(timedelta(hours=8)))
            days_left = (beijing_time - now).days
            
            return beijing_time, days_left
            
        except Exception as e:
            print(f"计算过期时间失败: {e}")
            return None, 0
    
    def update_cookie(self, input_str):
        """更新 cookie"""
        try:
            # 判断输入是否为 curl 命令
            if input_str.strip().startswith('curl'):
                cookie_str = self.extract_cookie_from_curl(input_str)
                if not cookie_str:
                    print("无法从 curl 命令中提取 cookie")
                    return False
            else:
                cookie_str = input_str
            
            print(f"\n提取到的 cookie: {cookie_str}")
            
            # 验证 cookie 格式
            if 'koa:sess=' not in cookie_str:
                print("无效的 cookie 格式")
                return False
                
            # 提取 koa:sess 的值
            sess = cookie_str.split('koa:sess=')[1].split(';')[0]
            
            try:
                # 解码检查
                decoded = base64.b64decode(sess).decode('utf-8')
                sess_data = json.loads(decoded)
                
                # 获取过期时间
                expire_time, days_left = self.calculate_expiry(sess_data.get('_expire', 0))
                
                # 获取用户信息
                user_id = sess_data.get('userId', 'unknown')
                
                # 更新 cookie 文件
                cookies = self.load_cookies()
                cookies['glados'] = {
                    'cookie': cookie_str,
                    'user_id': user_id,
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if self.save_cookies(cookies):
                    print(f"\nCookie 更新成功!")
                    print(f"用户 ID: {user_id}")
                    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"过期时间: {expire_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"剩余天数: {days_left} 天")
                    
                    if days_left <= 7:
                        print("\n⚠️ 警告: Cookie 即将在 7 天内过期!")
                    
                    return True
                    
            except Exception as e:
                print(f"Cookie 解析失败: {e}")
                return False
                
        except Exception as e:
            print(f"更新失败: {e}")
            return False

def main():
    manager = CookieManager()
    
    print("\nGLaDOS Cookie 管理工具")
    print("=" * 30)
    print("当前 Cookie 信息:")
    
    cookies = manager.load_cookies()
    if 'glados' in cookies:
        glados = cookies['glados']
        print(f"用户 ID: {glados.get('user_id', 'unknown')}")
        print(f"更新时间: {glados.get('update_time', 'unknown')}")
        print(f"过期时间: {glados.get('expire_time', 'unknown')}")
    else:
        print("未找到 Cookie 配置")
    
    print("\n" + "=" * 30)
    print("请输入 curl 命令或直接输入 cookie (直接回车退出):")
    
    # 读取多行输入
    lines = []
    while True:
        try:
            line = input()
            if not line:
                break
            lines.append(line)
        except EOFError:
            break
    
    user_input = '\n'.join(lines)
    
    if user_input.strip():
        manager.update_cookie(user_input)

if __name__ == "__main__":
    main()