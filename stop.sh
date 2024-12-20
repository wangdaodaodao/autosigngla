#!/bin/bash

# 检查 PID 文件
if [ ! -f "bot.pid" ]; then
    echo "GLaDOS Bot 未在运行"
    exit 0
fi

# 读取 PID
pid=$(cat bot.pid)

# 检查进程是否存在
if ! ps -p $pid > /dev/null 2>&1; then
    echo "GLaDOS Bot 未在运行 (PID 文件过期)"
    rm -f bot.pid
    exit 0
fi

# 发送终止信号
kill $pid
echo "已发送终止信号到 GLaDOS Bot (PID: $pid)"

# 等待进程结束
for i in {1..10}; do
    if ! ps -p $pid > /dev/null 2>&1; then
        rm -f bot.pid
        echo "GLaDOS Bot 已停止"
        exit 0
    fi
    sleep 1
done

# 如果进程仍在运行，强制终止
if ps -p $pid > /dev/null 2>&1; then
    kill -9 $pid
    rm -f bot.pid
    echo "GLaDOS Bot 已强制停止"
fi 