#!/bin/bash

# 进入脚本目录
cd /home/onwoywnooy/glados_checkin

# 设置 Python 路径
export PATH=/usr/local/bin:$PATH

# 执行签到脚本
python3 glados_checkin.py >> logs/checkin.log 2>&1