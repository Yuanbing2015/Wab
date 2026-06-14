# 📓 错题银行 (WrongAnswerBank)

> 一个父亲为孩子手作的、可生长 12 年的、AI 驱动的家庭学习陪伴系统。
> 把每一道错题变成一只可被打败、收藏、进化的怪物，
> 把每一次复习变成爸爸/妈妈/孩子之间的 5 分钟仪式。

[![Status](https://img.shields.io/badge/status-Sprint%200-blue)]() [![License](https://img.shields.io/badge/license-Personal-green)]()

---

## 🎯 项目概览

- **域名**：`wab.ybgames.cn`
- **属性**：私人项目，仅供家庭使用
- **目标用户**：男孩（一年级 / 现在）+ 女孩（小班 / 2-3 年后入场）+ 家长
- **核心理念**：错题不是「卡片」，是「知识盲点 + 错因 + 变式题」三位一体的成长画像

📖 **设计文档**：见 [`_bmad-output/planning-artifacts/brainstorming-session-wab-20260531.md`](_bmad-output/planning-artifacts/brainstorming-session-wab-20260531.md)

---

## 🏗 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Next.js 15 (SSR) + Tailwind + Zustand + TanStack Query |
| 后端 | Python 3.12 + FastAPI + SQLModel + Alembic |
| 数据库 | PostgreSQL 16 |
| 对象存储 | MinIO（S3 兼容） |
| LLM 文本 | DeepSeek-V3 |
| LLM 视觉 | DeepSeek-VL2（主） + Qwen-VL-Max（兜底） |
| TTS 朗读 | edge-tts（Microsoft Edge 神经语音，免费） |
| PDF 导出 | WeasyPrint |
| 反代 | 独立 Nginx |
| 容器化 | Docker Compose |

> 🖥 **目标服务器**：Ubuntu Server 24.04 LTS / 2 核 2GB / SSD 40GB / 2Mbps。
> 已针对 2GB 调优（PG `shared_buffers=128MB`、API 单 worker、构建限内存），**部署前必须配 4GB swap**，详见 [`docs/deployment.md`](docs/deployment.md)。

---

## 📂 仓库结构

```
WrongAnswerBank/
├── apps/
│   ├── api/                # FastAPI 后端
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   ├── core/       # 配置/数据库/安全
│   │   │   ├── models/     # SQLModel 模型
│   │   │   ├── routers/    # HTTP 路由
│   │   │   └── services/   # LLM/TTS/Storage/PDF/SRS
│   │   ├── alembic/        # 数据库迁移
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── web/                # Next.js 前端
│       ├── app/            # 路由页面
│       ├── lib/api.ts      # API 客户端
│       └── Dockerfile
├── infra/
│   ├── docker-compose.yml  # 5 服务编排
│   ├── postgres/           # PG 初始化与调优
│   ├── minio/              # MinIO bucket 初始化
│   ├── nginx-snippet.conf  # Nginx 反代片段（你服务器上用）
│   └── scripts/            # backup / restore / deploy
├── data/                    # 持久化数据（gitignored）
├── docs/                    # 架构与部署文档
├── _bmad/                   # BMAD 方法论资源
├── _bmad-output/            # BMAD 产物（脑暴/PRD/架构）
├── .env.example
└── README.md
```

---

## 🚀 本地开发

### 1. 准备环境变量

```bash
cp .env.example .env
# 编辑 .env，至少填入 DEEPSEEK_API_KEY
# DEEPSEEK_API_KEY 申请地址：https://platform.deepseek.com/
```

### 2. 启动全栈

```bash
cd infra
# 注意：.env 在项目根，需要 --env-file 指向它
docker compose --env-file ../.env up -d --build

# 查看日志
docker compose --env-file ../.env logs -f api
```

> 💡 **小技巧**：嫌每次 `--env-file ../.env` 麻烦？在 `infra/` 下做个软链：
> ```bash
> cd infra && ln -s ../.env .env
> ```
> 之后就可以直接 `docker compose up -d --build`

### 3. 访问

| 端点 | URL |
|---|---|
| Web 应用 | http://localhost:3000 |
| API 文档 | http://localhost:8000/api/docs |
| MinIO 控制台 | http://localhost:9090 |
| 健康检查 | http://localhost:8000/api/health |

### 4. 创建账号

打开 `http://localhost:3000/register` 注册男孩账号。

---

## 🌐 生产部署（你的服务器）

详见 [`docs/deployment.md`](docs/deployment.md)。简版流程：

```bash
# 1. 在服务器上克隆仓库
ssh your-server
git clone https://github.com/yuanbing/WrongAnswerBank.git
cd WrongAnswerBank
cp .env.example .env && vi .env  # 填入生产值

# 2. 启动
cd infra && docker compose up -d --build

# 3. 配置 Nginx（一次性）
sudo cp nginx-snippet.conf /etc/nginx/conf.d/wab.conf
sudo certbot --nginx -d wab.ybgames.cn  # 申请证书
sudo nginx -t && sudo systemctl reload nginx

# 4. 访问
open https://wab.ybgames.cn
```

---

## 🗓 开发路线（Sprint 状态）

- [x] **Sprint 0 — 脚手架** ✅（你正在这里）
- [ ] Sprint 1 — 用户与认证（基础完成，待联调测试）
- [ ] Sprint 2 — 录入闭环（拍照/扫描/批量）
- [ ] Sprint 3 — TTS 朗读底层
- [ ] Sprint 4 — 复习 P0 三件套（翻牌 + 家庭对战 + 兴趣化剧情）
- [ ] Sprint 5 — AI 生题 + PDF 导出
- [ ] Sprint 6 — 全量导出与备份

---

## 💾 备份

每日自动备份（建议加到 crontab）：

```bash
crontab -e
# 每天凌晨 2 点备份
0 2 * * * /path/to/WrongAnswerBank/infra/scripts/backup.sh
```

恢复：

```bash
./infra/scripts/restore.sh data/backup/2026-05-31_0200.tar.gz
```

---

## 📜 License

Personal use only. Built with 💛 by Yuanbing for his kids.
