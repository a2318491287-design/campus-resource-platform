# MUST Campus Academic Resource Sharing Platform — Backend

FastAPI + MariaDB 后端，提供完整的 REST API 实现 SDD v1.0 文档的所有功能。

## 内存预算

针对 **1GB RAM VPS**（已运行其他服务，约 245MB 空闲）做了 Docker 内存限制：

| 服务 | 限制 | 实际占用 |
|---|---|---|
| MariaDB 10.11 (`db`) | 180 MB | ~110-150 MB |
| FastAPI (`api`) | 80 MB | ~30-50 MB |
| **总计** | **260 MB** | **~140-200 MB** |

留有 50+ MB 余量。如果 OOM，只会杀掉 Docker 容器，不影响 lana scanner。

## 快速开始

### A. 在你的笔记本本地测试（SQLite，无需 Docker）

```bash
cd /Users/yuxianglian/Downloads/SAD_Project/backend

# 用 venv 隔离
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 用 SQLite（最简单）
export DATABASE_URL="sqlite:///./local.db"
export STORAGE_DIR="$(pwd)/storage"
mkdir -p storage
cp ../resources/* storage/

# 启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

另开终端 seed 数据：
```bash
source .venv/bin/activate
export DATABASE_URL="sqlite:///./local.db"
export STORAGE_DIR="$(pwd)/storage"
python -m app.seed
```

打开 [Prototype.html](../Prototype.html)，自动连接 `localhost:8000`。

### B. 部署到 VPS（生产）

**1. 上传所有文件到 VPS**（在笔记本上执行）：
```bash
cd /Users/yuxianglian/Downloads/SAD_Project/backend
bash upload_to_vps.sh
```

**2. SSH 到 VPS 并部署**：
```bash
ssh root@178.157.59.239
cd /opt/campus_resource_platform/backend
bash deploy.sh
```

**3. 配置 nginx 反向代理**：
```bash
cp nginx_campus.conf /etc/nginx/sites-available/campus_resource_platform
ln -sf /etc/nginx/sites-available/campus_resource_platform /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

**4. 验证**：
```bash
curl http://localhost:8000/health        # 直接访问 API
curl http://你的VPS的IP/health           # 经过 nginx
curl http://你的VPS的IP/                 # 看到 Prototype.html
```

## 架构

```
浏览器 (Prototype.html)
    ↓ HTTPS
nginx :80/443
    ├── /        → /opt/campus_resource_platform/web/Prototype.html
    └── /api/*   → reverse proxy → 127.0.0.1:8000 (FastAPI in Docker)
                                       ↓
                                MariaDB (Docker)
                                       ↓
                              ./storage/*.pdf,*.pptx
```

## 常用运维命令

```bash
# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f api
docker compose logs -f db

# 查看内存占用
docker stats --no-stream

# 重启
docker compose restart

# 完全停止
docker compose down

# 数据库备份
docker compose exec db sh -c 'exec mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" campus_resource_platform' > backup_$(date +%F).sql

# 进入数据库 shell
docker compose exec db mariadb -uroot -p campus_resource_platform

# 重新 seed（数据库会保留，只创建缺失的）
docker compose exec api python -m app.seed
```

## API 文档

启动后访问：
- Swagger UI：`http://你的VPS:8000/docs`（开发）或 `http://你的VPS/docs`（经 nginx）
- ReDoc：`http://你的VPS:8000/redoc`

## 主要 API 端点

| Method | Path | 描述 | 鉴权 |
|---|---|---|---|
| POST | `/api/auth/register` | 注册 | 无 |
| POST | `/api/auth/login` | 登录 | 无 |
| GET | `/api/auth/me` | 当前用户信息 | ✅ |
| GET | `/api/resources/search` | 搜索资源 | 无 |
| GET | `/api/resources/{id}` | 资源详情 | 无 |
| POST | `/api/resources/upload` | 上传资源 | ✅ |
| POST | `/api/resources/{id}/download` | 触发下载（扣分） | ✅ |
| GET | `/api/resources/{id}/file` | 下载实际文件 | ✅ |
| GET | `/api/resources` | 我的上传 | ✅ |
| GET | `/api/points/balance` | 积分余额 | ✅ |
| GET | `/api/points/history` | 积分流水 | ✅ |
| GET | `/api/points/leaderboard` | 月度排行榜 | 无 |
| POST | `/api/points/redeem` | 兑换 | ✅ |
| POST | `/api/ratings` | 提交评分 | ✅ |
| GET | `/api/ratings/{resource_id}` | 资源评分列表 | 无 |
| GET | `/api/admin/queue` | 待审核队列 | Admin |
| PATCH | `/api/admin/resources/{id}/review` | 审批 | Admin |

## 测试要点

### 1. 注册 + 登录
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"student_id":"1230099999","username":"测试用户","email":"test@must.edu.mo","password":"test123"}'
```

### 2. 测试原子积分扣减（关键点）
```bash
# 用 ab 工具发起 100 个并发下载请求
ab -n 100 -c 20 -m POST -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/resources/1/download

# 检查 DB 余额绝对不会变成负数
docker compose exec db mariadb -uroot -p -e "SELECT user_id, points_balance FROM users;"

# 检查 point_records 表的 balance_after 单调递减
docker compose exec db mariadb -uroot -p -e \
  "SELECT * FROM point_records WHERE user_id=1 ORDER BY created_at DESC LIMIT 20;"
```

### 3. 验证 SQL 真在跑
```bash
# 查看实时 query
docker compose exec db mariadb -uroot -p -e "SHOW PROCESSLIST;"

# 启用 general log（生产别开，调试时短期开）
docker compose exec db mariadb -uroot -p -e \
  "SET GLOBAL general_log = 'ON'; SET GLOBAL general_log_file='/tmp/queries.log';"
```

## 故障排查

**问题：Docker 起不来 / OOM**
```bash
# 检查可用内存
free -m

# 关闭其他服务腾内存（临时）
systemctl stop scanner.service
docker compose up -d
systemctl start scanner.service
```

**问题：API 返回 500**
```bash
docker compose logs api --tail=50
```

**问题：登录失败 "Invalid credentials"**
```bash
# 确认 seed 已执行
docker compose exec api python -m app.seed
```

**问题：上传后看不到资源**
- 资源默认 status=PENDING，需要 admin 审核
- 用预置账号 `1230020693`（is_admin=true）登录，进入 ⚙️ Admin 页面审批

## 安全提示

部署到生产前必做：
- [ ] 修改 `.env` 中的所有密码（默认值不安全）
- [ ] 配置 HTTPS（推荐 Let's Encrypt + certbot）
- [ ] 把 `CORS_ORIGINS` 从 `["*"]` 改为具体域名
- [ ] 启用防火墙（仅暴露 80/443，不暴露 8000 / 3306）
- [ ] 定期备份 `db_data` 卷
