-- WrongAnswerBank: Postgres 初始化（容器首次启动会自动跑）
-- 表结构由 alembic 负责迁移，这里只启用扩展。

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 时区
SET TIME ZONE 'Asia/Shanghai';
