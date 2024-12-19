import json
from datetime import datetime, timedelta
import base64
import logging

class CookieManager:
    def __init__(self, cookie_file="cookie.json"):
        self.cookie_file = cookie_file
        
    def save_cookie(self, cookie_str):
        """保存 cookie 和其过期时间"""
        try:
            # 解析 cookie 获取过期时间
            sess_data = cookie_str.split('koa:sess=')[1].split(';')[0]
            decoded_data = base64.b64decode(sess_data + '=' * (-len(sess_data) % 4))
            cookie_info = json.loads(decoded_data)
            
            expire_time = datetime.fromtimestamp(cookie_info.get('_expire', 0) / 1000)
            
            cookie_data = {
                "cookie": cookie_str,
                "expire_time": expire_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.cookie_file, 'w') as f:
                json.dump(cookie_data, f)
                
            logging.info(f"Cookie 已保存，有效期至: {expire_time}")
            
        except Exception as e:
            logging.error(f"保存 cookie 失败: {e}")
    
    def load_cookie(self):
        """加载 cookie 并检查是否过期"""
        try:
            with open(self.cookie_file, 'r') as f:
                data = json.load(f)
                
            expire_time = datetime.strptime(data["expire_time"], "%Y-%m-%d %H:%M:%S")
            
            # 如果还有7天就过期，发出警告
            if expire_time - datetime.now() < timedelta(days=7):
                logging.warning("Cookie 即将在7天内过期")
                
            return data["cookie"]
            
        except FileNotFoundError:
            logging.error("Cookie 文件不存在")
            return None
        except Exception as e:
            logging.error(f"加载 cookie 失败: {e}")
            return None 