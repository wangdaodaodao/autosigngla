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
        self.base_url = "http://wxpusher.zjiecode.com/api/send/message"
        
    def send(self, title, content):
        try:
            from config import PUSH_CONFIG
            
            data = {
                "appToken": self.token,
                "content": f"{title}\n\n{content}",
                "contentType": 1,
                "uids": [PUSH_CONFIG["wx_pusher"]["uid"]],
                "url": "https://glados.space"
            }
            
            logging.info("准备发送推送")
            response = requests.post(self.base_url, json=data)
            result = response.json()
            
            if result.get("code") == 1000:
                logging.info("推送发送成功")
                return True
            else:
                logging.error(f"推送失败: {result}")
                return False
                
        except Exception as e:
            logging.error(f"推送异常: {e}")
            return False 