#!/bin/bash
# =====================================================
# WrongAnswerBank — 每日备份脚本
# 备份内容：PostgreSQL dump + MinIO 全部对象
# 保留：30 天滚动
# 用法：在 crontab 中加：0 2 * * * /path/to/repo/infra/scripts/backup.sh
# =====================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
BACKUP_DIR="$PROJECT_ROOT/data/backup"
DATE=$(date +%Y-%m-%d_%H%M)
TMP="$BACKUP_DIR/$DATE"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ 未找到 .env: $ENV_FILE"
  exit 1
fi
# shellcheck disable=SC2046
export $(grep -v '^#' "$ENV_FILE" | xargs)

mkdir -p "$TMP"

echo "[1/3] PostgreSQL dump..."
docker exec wab-postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc \
  > "$TMP/wab.dump"

echo "[2/3] MinIO mirror..."
docker run --rm --network wab-net \
  -v "$TMP:/backup" \
  -e "MC_HOST_wab=http://${MINIO_ROOT_USER}:${MINIO_ROOT_PASSWORD}@minio:9000" \
  minio/mc:latest mirror --quiet --overwrite wab "/backup/minio"

echo "[3/3] 打包并清理..."
cd "$BACKUP_DIR"
tar czf "${DATE}.tar.gz" "$DATE"
rm -rf "$DATE"

# 滚动保留 30 天
find "$BACKUP_DIR" -maxdepth 1 -name "*.tar.gz" -mtime +30 -delete

echo "✅ 备份完成: $BACKUP_DIR/${DATE}.tar.gz"
