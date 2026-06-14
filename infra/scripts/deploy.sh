#!/bin/bash
# =====================================================
# WrongAnswerBank — 生产部署脚本（在你的服务器上执行）
# 用法：./infra/scripts/deploy.sh
# =====================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -f .env ]]; then
  echo "❌ .env 不存在，请先 cp .env.example .env 并填入真实值"
  exit 1
fi

echo "[1/5] 拉取最新代码..."
git pull --ff-only

echo "[2/5] 构建镜像..."
cd infra
docker compose --env-file ../.env build

echo "[3/5] 启动服务..."
docker compose --env-file ../.env up -d

echo "[4/5] 等待 API 容器就绪并执行迁移..."
sleep 5
docker compose --env-file ../.env exec api alembic upgrade head

echo "[5/5] 服务状态..."
docker compose --env-file ../.env ps

echo "✅ 部署完成。访问：https://wab.ybgames.cn"
