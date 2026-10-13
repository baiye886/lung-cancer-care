#!/bin/bash
# 肺康守护 (Recovery Atlas) 腾讯云 Linux 后台运行与重启脚本
cd "$(dirname "$0")"

PID=$(pgrep -f "python.*server.py")
if [ -n "$PID" ]; then
    echo "发现正在运行的旧进程 (PID: $PID)，正在平滑终止..."
    kill -15 $PID
    sleep 1
fi

echo "正在启动新服务..."
nohup python3 server.py > server.log 2>&1 &
NEW_PID=$!

sleep 1
if ps -p $NEW_PID > /dev/null; then
    echo "=================================================="
    echo "服务已成功在后台启动！PID: $NEW_PID"
    echo "日志文件: $(pwd)/server.log"
    echo "可执行 tail -f server.log 查看实时访问日志"
    echo "=================================================="
else
    echo "启动失败，请检查 server.log 报错信息！"
fi
