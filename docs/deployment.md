# 部署指引 — Ubuntu 24.04 全新轻量服务器

> 目标：把 WrongAnswerBank 从零部署到 `wab.ybgames.cn`
>
> **目标服务器**：Ubuntu Server 24.04 LTS / 2 核 2GB / SSD 40GB / 2Mbps·100GB/月 / 全新空机

---

## ⚠️ 2GB 内存关键须知（先读）

| 事项 | 说明 |
|---|---|
| **必须加 4GB swap** | 否则 `npm run build` 会因内存尖峰 OOM 被杀。见 §2。 |
| 已做的调优 | PG `shared_buffers=128MB`、API `--workers 1`、Web 构建 `--max-old-space-size=1024` |
| 运行时预算 | PG ~250MB + MinIO ~200MB + API ~200MB + Web ~250MB + 系统 ~350MB ≈ 1.25GB，余 ~750MB |
| 构建策略 | 构建慢（2Mbps + 2核），已配国内镜像源；建议**逐个服务构建**避免并发抢内存 |

---

## 1. 系统初始化

```bash
ssh root@<服务器IP>

# 更新系统
apt update && apt upgrade -y

# 基础工具
apt install -y curl git vim ufw

# 时区
timedatectl set-timezone Asia/Shanghai
```

---

## 2. 创建 4GB Swap（关键步骤，不可跳过）

```bash
# 创建 4GB swap 文件
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 开机自动挂载
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 降低 swappiness（优先用物理内存，swap 仅兜底）
sysctl vm.swappiness=10
echo 'vm.swappiness=10' >> /etc/sysctl.conf

# 验证
free -h
# 应看到 Swap: 4.0Gi
```

---

## 3. 安装 Docker（Ubuntu 24.04 官方源）

```bash
# 卸载可能存在的旧版本
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do
  apt remove -y $pkg 2>/dev/null || true
done

# 安装 Docker 官方 GPG key
apt install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 验证
docker --version
docker compose version
```

### 3.1（可选）配置 Docker 国内镜像加速

2Mbps 拉镜像很慢，建议配镜像加速器：

```bash
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live"
  ],
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
EOF
systemctl restart docker
```

> 💡 镜像加速器地址时常变动，如失效可搜索"Docker 镜像加速 2026"获取可用源。

---

## 4. 防火墙

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status
```

> 注意：3000/8000/9000/9090 等端口**不开放**，它们只监听 `127.0.0.1`，由 Nginx 反代对外。

---

## 5. 拉取代码与配置

```bash
cd /opt
git clone <你的仓库地址> WrongAnswerBank
cd WrongAnswerBank

cp .env.example .env
vi .env
```

**必改字段**：

```ini
POSTGRES_PASSWORD=<openssl rand -hex 32>
MINIO_ROOT_PASSWORD=<openssl rand -hex 32>
API_SECRET_KEY=<openssl rand -hex 32>
NEXTAUTH_SECRET=<openssl rand -hex 32>
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

MINIO_PUBLIC_ENDPOINT=https://wab.ybgames.cn/files
NEXT_PUBLIC_API_BASE_URL=https://wab.ybgames.cn/api
NEXTAUTH_URL=https://wab.ybgames.cn
API_CORS_ORIGINS=https://wab.ybgames.cn
```

生成随机串：`openssl rand -hex 32`

---

## 6. 构建与启动

> ⚠️ 2GB 内存：**逐个构建**，避免 web 和 api 同时编译抢内存。

```bash
cd /opt/WrongAnswerBank/infra

# .env 在项目根，做个软链省事
ln -s ../.env .env

# 先单独构建 api（Python 依赖）
docker compose build api

# 再单独构建 web（Node 构建吃内存，已限制 1GB + 有 swap 兜底）
docker compose build web

# 启动全部
docker compose up -d

# 观察启动
docker compose ps -a
docker compose logs -f api
```

期望结果：

```
NAME             STATUS                    PORTS
wab-postgres     Up (healthy)
wab-minio        Up (healthy)              127.0.0.1:9000->9000, 127.0.0.1:9090->9090
wab-minio-init   Exited (0)
wab-api          Up (healthy)              127.0.0.1:8000->8000
wab-web          Up                        127.0.0.1:3000->3000
```

验证：

```bash
curl -s http://127.0.0.1:8000/api/health
# {"status":"ok","service":"wab-api","version":"0.1.0"}
curl -sI http://127.0.0.1:3000 | head -1
# HTTP/1.1 200 OK
```

---

## 7. 安装 Nginx + SSL

```bash
apt install -y nginx

# 拷贝反代配置
cp /opt/WrongAnswerBank/infra/nginx-snippet.conf /etc/nginx/conf.d/wab.conf

# 先申请证书（certbot 会临时改 nginx 配置）
apt install -y certbot python3-certbot-nginx
certbot --nginx -d wab.ybgames.cn

# 测试并重载
nginx -t
systemctl reload nginx
systemctl enable nginx
```

> 前提：`wab.ybgames.cn` 的 DNS A 记录已指向本服务器 IP。

---

## 8. 验收

浏览器访问：`https://wab.ybgames.cn`

应看到「📓 错题银行」首页。进入 `/register` 注册男孩账号即可。

---

## 9. 日常运维

### 9.1 备份（cron）

```bash
crontab -e
# 每天凌晨 2 点
0 2 * * * /opt/WrongAnswerBank/infra/scripts/backup.sh >> /var/log/wab-backup.log 2>&1
```

### 9.2 资源监控

```bash
docker stats --no-stream
free -h            # 看 swap 使用情况
df -h /            # 看磁盘
```

**预警线**：若物理内存长期 > 1.8GB 且 swap 使用 > 2GB，说明吃紧，处理顺序：
1. 确认 web/api 没有内存泄漏（`docker stats` 观察增长）
2. PG `shared_buffers` 128MB → 96MB
3. 极端情况：考虑升级到 4GB 套餐

### 9.3 升级代码

```bash
cd /opt/WrongAnswerBank
git pull --ff-only
cd infra
docker compose build api && docker compose build web   # 逐个构建
docker compose up -d
docker compose exec api alembic upgrade head
```

### 9.4 进容器调试

```bash
docker compose exec api bash
docker compose exec postgres psql -U wab -d wab
```

---

## 10. 故障排查

| 现象 | 排查 |
|---|---|
| `npm run build` 被 Killed | swap 没配！回到 §2 加 4GB swap 重试 |
| 镜像拉取超时 | 配 §3.1 镜像加速器；或耐心等（2Mbps 拉 PG/MinIO 镜像约 5-10 分钟） |
| 502 Bad Gateway | `docker compose ps` 看容器状态；`curl http://127.0.0.1:3000` 测本地直连 |
| api 卡在迁移 | `docker compose logs api`；常见 PG 密码错或未就绪 |
| 上传图片 403 | MinIO bucket 未建 → `docker compose run --rm minio-init` |
| 内存吃紧 OOM | `docker stats`；确认 swap 生效 `free -h` |
| certbot 失败 | 确认 DNS 已解析、80 端口开放、域名能 ping 通 |
