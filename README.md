# 校园学术资源共享平台

**Campus Academic Resource Sharing Platform**

System Analysis and Design · Final Group Project · Spring 2026
School of Business · Macau University of Science and Technology

**团队：** 连宇翔 1230020693 · 郁凯杰 1230020426 · 陈瀚中 1230032209
**指导老师：** Dr. CHE Pak Hou (Howard)

---

## 🌐 在线访问

```
https://signing-isle-printed-shapes.trycloudflare.com
```

**演示账号：** 学号 `1230000000` · 密码 `demo123`（普通用户，含 100 积分）

---

## 📦 目录结构

```
SAD_Project/
│
├── 📄 交付物（11 份，可直接交 Moodle）
│   ├── Requirements_Analysis_Document.docx    需求分析文档（25 FR + 12 NFR + UML）
│   ├── System_Design_Document.docx            系统设计文档（三层架构 + DB schema）
│   ├── Progress_Report_1.docx                 第一阶段进度报告（Week 7）
│   ├── Progress_Report_2.docx                 第二阶段进度报告（Week 13）
│   ├── Prototype_Specification.docx           原型说明文档
│   ├── Test_Validation_Report.docx            测试与验证报告
│   ├── Final_Project_Report.docx              最终项目报告（综合性）
│   ├── Presentation_Script.docx               15 分钟演讲讲稿
│   ├── Final_Presentation.pptx                演示 PPT（编辑式 × 多彩调色板）
│   ├── Final_Presentation.html                演示 PPT（杂志风网页版，靛蓝瓷主题）
│   └── Prototype.html                         高保真交互原型（接真实后端）
│
├── 📂 backend/                                 真实后端代码（部署在 VPS）
│   ├── app/                                       FastAPI 应用源码
│   │   ├── main.py                                  入口
│   │   ├── config.py                                配置（积分常量、相关性权重）
│   │   ├── database.py                              SQLAlchemy 连接池
│   │   ├── models.py                                ORM 模型（8 张表）
│   │   ├── schemas.py                               Pydantic API 模型
│   │   ├── auth.py                                  JWT 认证 + bcrypt
│   │   ├── points_engine.py                         积分原子事务引擎
│   │   ├── search_engine.py                         相关性排序算法
│   │   ├── seed.py                                  种子数据脚本
│   │   └── routers/                                 5 个路由模块
│   ├── schema.sql                                 MySQL DDL
│   ├── Dockerfile                                 容器构建配置
│   ├── docker-compose.yml                         MariaDB + API 编排（含内存限额）
│   ├── nginx_campus.conf                          nginx 反向代理配置
│   ├── requirements.txt                           Python 依赖锁定
│   ├── deploy.sh                                  一键部署脚本
│   ├── upload_to_vps.sh                           笔记本上传 VPS 脚本
│   ├── README.md                                  后端运维文档
│   ├── .env.example                               环境变量模板
│   ├── storage/                                   服务端文件存储（9 份课程资源副本）
│   ├── local.db                                   本地 SQLite（开发用，可忽略）
│   └── .venv/                                     Python 虚拟环境（不要提交）
│
├── 📂 resources/                               9 份课程资源原文件
│   ├── SAD_Ch01_Introduction.pptx
│   ├── SAD_Ch04_Requirements_Modeling.pptx
│   ├── MySQL_Installation_Guide.pdf
│   ├── DataMining_Week01_Introduction.pdf
│   ├── DataMining_Week04.pdf
│   ├── Forecasting_Lecture01_Introduction.pdf
│   ├── Forecasting_Lecture02_Data_Patterns.pdf
│   ├── Ecommerce_Ch01_Introduction.pdf
│   └── Ecommerce_Ch04.pdf
│
├── 📂 ppt_assets/                              网页 PPT 资源（被 Final_Presentation.html 引用）
│   └── motion.min.js                              Motion One 动效库（离线副本）
│
└── 📂 scripts/                                 文档生成脚本（开发用，可不交）
    ├── gen_requirements.py                        → Requirements_Analysis_Document.docx
    ├── gen_system_design.py                       → System_Design_Document.docx
    ├── gen_progress_reports.py                    → Progress_Report_1.docx + 2.docx
    ├── gen_prototype_spec.py                      → Prototype_Specification.docx
    ├── gen_test_report.py                         → Test_Validation_Report.docx
    ├── gen_final_report.py                        → Final_Project_Report.docx
    ├── gen_speech_script.py                       → Presentation_Script.docx
    └── gen_presentation.py                        → Final_Presentation.pptx
```

---

## 🎯 项目核心

**两大功能：**
1. **优化精准检索**（功能改进）— 课程代码 + 学年 + 类型 + 评分 多维度筛选 · 综合相关性排序
2. **积分激励体系**（新功能）— 注册送 100 · 上传/被下载/被好评得分 · 兑换下载次数和置顶

**真实部署：**
- VPS（1GB AlmaLinux）+ Docker（MariaDB 180MB · FastAPI 160MB）
- Cloudflare Tunnel 提供 HTTPS
- 实测 100 并发 0 错误 · 87ms 响应 · 1000 笔原子事务 0 race condition

---

## 📋 提交 Moodle 时打包哪些

最小提交集（推荐）：
- 全部根目录 `.docx`（8 份）
- `Final_Presentation.pptx` 或 `Final_Presentation.html`（二选一或都交）
- `Prototype.html` + `ppt_assets/`（原型可在浏览器打开演示）
- `resources/`（9 份课程资源）

完整提交集（含后端代码）：
- 上面所有 + `backend/` 目录（**排除** `backend/.venv/` 和 `backend/local.db`）
- `scripts/` 目录（生成脚本，可选）

打包命令（自动排除）：
```bash
cd ~/Documents/系统分析与设计
zip -r SAD_Project_Submission.zip SAD_Project \
  -x "*.venv/*" "*__pycache__/*" "*local.db" "*.pyc"
```

---

## 🚀 本地启动方法

### 仅看 PPT / 原型（无需启动后端）
```bash
open Final_Presentation.html        # 网页 PPT
open Final_Presentation.pptx        # 桌面 PPT
open Prototype.html                 # 高保真原型（连云端真后端）
```

### 启动本地后端（开发调试）
```bash
cd backend
source .venv/bin/activate
DATABASE_URL="sqlite:///./local.db" \
STORAGE_DIR="$(pwd)/storage" \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

详见 `backend/README.md`。

---

## 📊 项目数据

| 维度 | 数据 |
|---|---|
| 文档总字数 | ~50,000 字 |
| 代码行数 | ~3,500 行（FastAPI + HTML + JS） |
| 真实部署 | VPS · 24/7 在线 · HTTPS |
| 测试覆盖 | 32 用例 · 100% 通过 · 100 并发实测 |
| 用户调研 | 47 名学生 + 8 次深访 |
| 项目时长 | 2026.03.14 – 2026.06.30 |
