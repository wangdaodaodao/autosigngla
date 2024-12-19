#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WxPusher推送服务
"""

import requests
import logging

class WxPusher:
    def __init__(self, token):
        self.token = token
        self.push_url = "http://wxpusher.zjiecode.com/api/send/message"
    
    def send(self, title, content=""):
        try:
            # 如果title为空，直接使用content作为完整消息
            message = content if not title else f"{title}\n\n{content}"
            
            data = {
                "appToken": self.token,
                "content": message,
                "contentType": 1,
                "uids": ["UID_ikc0HQoKmCw9ln88ZmRZSQOguR15"],
                "url": "https://glados.space"
            }
            
            logging.info(f"准备发送推送, URL: {self.push_url}")
            logging.info(f"推送数据: {data}")
            
            response = requests.post(self.push_url, json=data, timeout=30)  # 增加超时时间
            result = response.json()
            logging.info(f"推送响应: {result}")
            
            if result.get("success"):
                logging.info("WxPusher推送成功")
                return True
            else:
                logging.error(f"WxPusher推送失败: {result.get('msg')}")
                return False
                
        except Exception as e:
            logging.error(f"WxPusher推送异常: {str(e)}")
            return False 