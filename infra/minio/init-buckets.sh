#!/bin/sh
# WrongAnswerBank — MinIO bucket 初始化脚本
# 容器启动时执行，幂等，重复跑无副作用
set -e

echo "[minio-init] 等待 MinIO 就绪..."
until /usr/bin/mc alias set wab "http://minio:9000" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1; do
  sleep 1
done

for bucket in "$MINIO_BUCKET_UPLOADS" "$MINIO_BUCKET_TTS" "$MINIO_BUCKET_PDFS"; do
  if /usr/bin/mc ls "wab/$bucket" >/dev/null 2>&1; then
    echo "[minio-init] Bucket $bucket 已存在，跳过"
  else
    echo "[minio-init] 创建 Bucket: $bucket"
    /usr/bin/mc mb "wab/$bucket"
    /usr/bin/mc anonymous set none "wab/$bucket"
  fi
done

echo "[minio-init] ✅ 完成"
