FROM python:3.12-slim

WORKDIR /app

# WeasyPrint 系统依赖 + 中文字体
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libssl-dev \
    libxml2 \
    libxslt-dev \
    fonts-noto-cjk \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# 2Mbps 带宽：用国内镜像源加速（如在海外可注释掉这行）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 容器启动时自动跑迁移再起服务
# 2GB 服务器：单 worker 即可，家庭使用并发极低
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1"]
