#!/bin/bash

# 定义变量
DEPLOY_PATH="/home/onwoywnooy/glados_checkin"
BACKUP_PATH="${DEPLOY_PATH}/backup/$(date +%Y%m%d_%H%M%S)"

# 创建备份目录
mkdir -p "$BACKUP_PATH"

# 备份当前代码
echo "备份当前代码..."
cp -r "${DEPLOY_PATH}"/* "$BACKUP_PATH"

# 同步新代码
echo "更新代码..."
rsync -av --exclude '.git' \
    --exclude 'backup' \
    --exclude 'logs' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    ./ "${DEPLOY_PATH}/"

# 设置权限
echo "设置权限..."
chmod +x "${DEPLOY_PATH}"/*.py
chmod +x "${DEPLOY_PATH}"/*.sh

# 重启服务
echo "重启服务..."
cd "${DEPLOY_PATH}"
pkill -f "python3 glados_checkin.py"
nohup python3 glados_checkin.py > /dev/null 2>&1 &

echo "部署完成！"