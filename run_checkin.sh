#!/bin/bash

# 进入脚本所在目录
cd /home/onwoywnooy/glados_checkin

# 获取 Python3 的实际路径
PYTHON_PATH=$(which python3)

# 执行签到脚本
$PYTHON_PATH glados_checkin.py 