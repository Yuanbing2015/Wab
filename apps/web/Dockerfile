FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
# 2Mbps 带宽：用国内镜像源加速（如在海外可注释掉这行）
RUN npm config set registry https://registry.npmmirror.com
RUN npm install --legacy-peer-deps

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
# 2GB 服务器：限制 Node 构建内存峰值，配合 swap 防 OOM
ENV NODE_OPTIONS=--max-old-space-size=1024
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
