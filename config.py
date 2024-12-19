# 服务器配置
SERVER_CONFIG = {
    "host": "panel15.serv00.com",
    "env": "production",
    "deploy_path": "/home/onwoywnooy/glados_checkin",
    "timezone": "Asia/Shanghai"
}

# 定时任务配置
SCHEDULE_CONFIG = {
    "checkin_time_start": "14:25",
    "checkin_time_end": "14:25",
    "retry_times": 3,
    "retry_interval": 300
}

# Server酱推送配置
PUSH_CONFIG = {
    "server_chan": {
        "send_key": "SCT265538T8vcj9P3kpTRStO1wDWmyy0Xh",
        "enable": False,  # 禁用Server酱
    },
    
    # WxPusher配置
    "wx_pusher": {
        "token": "AT_DA1IXmogP80uJiZlFtU4ZhAmVvQdUJK4",
        "uid": "UID_ikc0HQoKmCw9ln88ZmRZSQOguR15",  # 替换为您的UID
        "enable": True,
    },
    
    # 推送策略
    "push_on_success": True,
    "push_on_failure": True
}

# GLaDOS 签到配置
GLADOS_CONFIG = {
    "cookie": (
        "koa:sess=eyJ1c2VySWQiOjU2ODgyMiwiX2V4cGlyZSI6MTc2MDQ5MjgyNDY2NSwiX21heEFnZSI6MjU5MjAwMDAwMDB9; "
        "koa:sess.sig=ie30NT4rhnL7JhBaRuUerXgTdBE"
    ),
    "enable": True,          # 是否启用GLaDOS签到
    "check_interval": 86400  # 签到间隔(秒)，默认24小时
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",        # 日志级别
    "file": "checkin.log",  # 日志文件名
    "max_size": 10485760,   # 日志文件大小限制，默认10MB
    "backup_count": 5       # 保留的日志文件数量
}

