# GLaDOS 自动签到

自动执行 GLaDOS 每日签到并通过微信推送结果。

## 功能特点

- 自动签到：每天在指定时间段内随机执行签到
- Telegram推送：使用 Telegram Bot 推送签到结果
- 失败重试：签到失败自动重试
- 详细日志：记录完整的运行日志

## 文件说明

- `config.py`: 配置文件，包含各种设置
- `glados_notify.py`: 主程序，实现签到和多平台通知功能
- `tgbot_sender.py`: Telegram Bot 消息发送服务
- `tgbot_config.py`: Telegram Bot 配置文件
- `tgbot_test.py`: Telegram Bot 测试工具
- `scheduler.py`: 定时任务管理
- `deploy.sh`: 部署脚本

## 部署方法

1. 配置文件 

## 使用方法

1. 配置 config.py
2. 运行签到脚本：