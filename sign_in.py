#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GLaDOS 自动签到主程序
"""


import logging
from datetime import datetime
from glados_checkin import GladosCheckin
from push_service import create_push_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='sign_in.log'
)

def run_glados_checkin():
    """运行 GLaDOS 签到"""
    from config import GLADOS_CONFIG, PUSH_CONFIG
    
    # 创建推送服务
    push = create_push_service(PUSH_CONFIG)
    
    # 执行签到
    glados = GladosCheckin(GLADOS_CONFIG['cookie'])
    success, message = glados.checkin()
    
    # 准备推送内容
    title = "GLaDOS 签到成功 ✅" if success else "GLaDOS 签到失败 ❌"
    content = f"""
    ### 签到详情
    
    - 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    - 主机: server00
    
    {message}
    """
    
    # 发送通知
    push.send(title, content)

if __name__ == "__main__":
    run_glados_checkin() 