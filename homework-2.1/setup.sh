#!/bin/bash

# ============================================
# 任务脚本 - Linux 练习
# ============================================

set -e  # 遇到错误立即退出

echo "===== 开始执行任务 ====="

# 1. 创建 linux_practice 文件夹，内含 docs 和 backup 子目录
echo "[1/6] 创建目录结构..."
mkdir -p linux_practice/docs linux_practice/backup

# 2. 在 docs 目录下创建三个文件
echo "[2/6] 创建文件..."
touch linux_practice/docs/readme.txt linux_practice/docs/notes.log linux_practice/docs/temp.tmp

# 3. 删除 temp.tmp，将 notes.log 重命名为 daily_report.txt
echo "[3/6] 删除 temp.tmp 并重命名 notes.log..."
rm linux_practice/docs/temp.tmp
mv linux_practice/docs/notes.log linux_practice/docs/daily_report.txt

# 4. 向 daily_report.txt 写入内容
echo "[4/6] 写入 daily_report.txt..."
echo "Project Status: Active" > linux_practice/docs/daily_report.txt
date >> linux_practice/docs/daily_report.txt

# 5. 将 docs 目录下的所有 .txt 文件复制到 backup
echo "[5/6] 复制 .txt 文件到 backup..."
cp linux_practice/docs/*.txt linux_practice/backup/

# 6. 将 backup 目录下所有文件设为只读，并输出提示
echo "[6/6] 设置只读权限..."
chmod 444 linux_practice/backup/*
echo ""
echo "===== 任务完成 ====="
echo ""

# 输出每个文件的提示信息
for file in linux_practice/backup/*; do
    filename=$(basename "$file")
    echo "Archive Complete. File [$filename] is now read-only."
done
