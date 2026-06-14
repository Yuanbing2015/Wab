#!/bin/bash
# =====================================================
# WrongAnswerBank — 备份恢复脚本
# 用法：./infra/scripts/restore.sh data/backup/2026-05-31_0200.tar.gz
# =====================================================
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "用法: $0 <backup-file.tar.gz>"
  exit 1
fi

BACKUP_FILE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

# shellcheck disable=SC2046
export $(grep -v '^#' "$ENV_FILE" | xargs)

TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

echo "[1/3] 解压备份..."
tar xzf "$BACKUP_FILE" -C "$TMP_DIR"
EXTRACTED=$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -1)

echo "⚠️  即将清空数据库 $POSTGRES_DB 并恢复，按 Ctrl+C 可取消（5 秒）..."
sleep 5

echo "[2/3] PostgreSQL 恢复..."
docker exec -i wab-postgres dropdb -U "$POSTGRES_USER" --if-exists "$POSTGRES_DB"
docker exec -i wab-postgres createdb -U "$POSTGRES_USER" "$POSTGRES_DB"
docker exec -i wab-postgres pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  < "$EXTRACTED/wab.dump"

echo "[3/3] MinIO 恢复..."
docker run --rm --network wab-net \
  -v "$EXTRACTED:/restore" \
  -e "MC_HOST_wab=http://${MINIO_ROOT_USER}:${MINIO_ROOT_PASSWORD}@minio:9000" \
  minio/mc:latest mirror --quiet --overwrite "/restore/minio" wab

echo "✅ 恢复完成"
