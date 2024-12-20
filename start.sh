#!/bin/bash

# 检查是否已运行
if [ -f "bot.pid" ]; then
    pid=$(cat bot.pid)
    if ps -p $pid > /dev/null 2>&1; then
        echo "GLaDOS Bot 已在运行 (PID: $pid)"
        exit 1
    else
        rm -f bot.pid
    fi
fi

# 创建日志目录
mkdir -p logs

# 启动程序
nohup python3 main.py --daemon > /dev/null 2>&1 &

# 等待几秒确认启动
sleep 2

# 检查是否成功启动
if [ -f "bot.pid" ]; then
    pid=$(cat bot.pid)
    if ps -p $pid > /dev/null 2>&1; then
        echo "GLaDOS Bot 已成功启动 (PID: $pid)"
        exit 0
    fi
fi

echo "GLaDOS Bot 启动失败"
exit 1 