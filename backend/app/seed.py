"""
Seed script — populate the database with the user's 9 course resources.

Run after the API has started (which auto-creates tables).
    python -m app.seed
"""
import os
import shutil
from datetime import datetime

from .config import settings
from .database import SessionLocal, engine, Base
from .models import User, Resource, Tag, ResourceTag, PointRecord
from .auth import hash_password


SEED_USER = {
    "student_id": "1230020693",
    "username": "连宇翔",
    "email": "lian.yuxiang@must.edu.mo",
    "password": "demo123",
    "is_admin": True,  # also admin so you can review uploads
}

# 9 resources matching the files in Downloads/SAD_Project/resources/
SEED_RESOURCES = [
    {
        "title": "System Analysis & Design — Chapter 1: Introduction",
        "description": ("Tilley 12e 教材 Chapter 1 官方讲义。涵盖系统分析师的角色、SDLC 概览、"
                        "敏捷与瀑布方法对比、关键术语定义。本章节为整门课的入门基础。"),
        "file_name": "SAD_Ch01_Introduction.pptx",
        "file_type": "PPTX",
        "course_code": "BBAZ16604",
        "academic_year": 2026,
        "resource_type": "LECTURE",
        "tags": ["课程讲义", "Tilley", "Ch1", "Introduction"],
        "pinned": True,
    },
    {
        "title": "System Analysis & Design — Chapter 4: Requirements Modeling",
        "description": ("Tilley 12e Chapter 4 官方讲义。深入讲解需求建模技术，包括 JAD、RAD、"
                        "用例图、数据流图等。是项目阶段的关键参考材料。"),
        "file_name": "SAD_Ch04_Requirements_Modeling.pptx",
        "file_type": "PPTX",
        "course_code": "BBAZ16604",
        "academic_year": 2026,
        "resource_type": "LECTURE",
        "tags": ["课程讲义", "Tilley", "Ch4", "需求建模"],
    },
    {
        "title": "MySQL 8.0 Installation Guide — 完整安装与配置手册",
        "description": ("MySQL 8.0 详细安装手册。覆盖 Windows / macOS 双平台安装步骤、"
                        "初始配置、root 密码设置、Workbench 连接、常见问题排查。"),
        "file_name": "MySQL_Installation_Guide.pdf",
        "file_type": "PDF",
        "course_code": "BBAZ16604",
        "academic_year": 2026,
        "resource_type": "GUIDE",
        "tags": ["MySQL", "数据库", "操作指南", "安装"],
    },
    {
        "title": "Data Mining — Week 1 Introduction",
        "description": ("数据挖掘课程第一周讲义。涵盖数据挖掘基本概念、应用领域、"
                        "KDD 流程、CRISP-DM 方法论。"),
        "file_name": "DataMining_Week01_Introduction.pdf",
        "file_type": "PDF",
        "course_code": "BBAZ16603",
        "academic_year": 2026,
        "resource_type": "LECTURE",
        "tags": ["数据挖掘", "Week1", "Introduction", "KDD"],
    },
    {
        "title": "Data Mining — Week 4",
        "description": "数据挖掘第四周讲义。深入讨论分类算法基础、决策树原理、特征选择策略。",
        "file_name": "DataMining_Week04.pdf",
        "file_type": "PDF",
        "course_code": "BBAZ16603",
        "academic_year": 2026,
        "resource_type": "LECTURE",
        "tags": ["数据挖掘", "Week4", "决策树", "分类"],
    },
    {
        "title": "Business Forecasting — Lecture 1: Introduction to Forecasting",
        "description": "商务预测课程第一讲。介绍预测的基本概念、定性与定量方法分类、预测的商业价值。",
        "file_name": "Forecasting_Lecture01_Introduction.pdf",
        "file_type": "PDF",
        "course_code": "BBAZ16605",
        "academic_year": 2026,
        "resource_type": "LECTURE",
        "tags": ["商务预测", "Lecture1", "Introduction"],
    },
    {
        "title": "Business Forecasting — Lecture 2: Exploring Data Patterns",
        "description": "商务预测第二讲。讲解时间序列数据的可视化探索、识别趋势、季节性、周期性模式。",
        "file_name": "Forecasting_Lecture02_Data_Patterns.pdf",
        "file_type": "PDF",
        "course_code": "BBAZ16605",
        "academic_year": 2026,
        "resource_type": "LECTURE",
        "tags": ["商务预测", "Lecture2", "时间序列", "数据模式"],
    },
    {
        "title": "E-Commerce — Chapter 1: Introduction to E-Commerce",
        "description": ("电子商务课程第一章。Laudon-Traver 教材原版讲义，介绍电商发展历程、"
                        "八大独特技术特征、商业模式分类。"),
        "file_name": "Ecommerce_Ch01_Introduction.pdf",
        "file_type": "PDF",
        "course_code": "BBAZ16607",
        "academic_year": 2026,
        "resource_type": "LECTURE",
        "tags": ["电子商务", "Ch1", "Introduction", "Laudon-Traver"],
    },
    {
        "title": "E-Commerce — Chapter 4",
        "description": "电子商务课程第四章讲义。讲解电商基础设施、Web 技术、移动平台、客户端技术。",
        "file_name": "Ecommerce_Ch04.pdf",
        "file_type": "PDF",
        "course_code": "BBAZ16607",
        "academic_year": 2026,
        "resource_type": "LECTURE",
        "tags": ["电子商务", "Ch4", "技术架构"],
    },
]


def main():
    """
    Run seeding. Idempotent — skip if user already exists.
    The actual files should already be in /app/storage (or local equivalent)
    via the docker-compose volume mount.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    from datetime import datetime, timedelta
    now = datetime.utcnow()

    try:
        # Create the user (or skip if exists)
        existing = db.query(User).filter(User.student_id == SEED_USER["student_id"]).first()
        if existing:
            print(f"User {SEED_USER['student_id']} already exists, user_id={existing.user_id}")
            user = existing
        else:
            user = User(
                student_id=SEED_USER["student_id"],
                username=SEED_USER["username"],
                email=SEED_USER["email"],
                password_hash=hash_password(SEED_USER["password"]),
                is_admin=SEED_USER["is_admin"],
                points_balance=100,  # Welcome bonus — same rule as new registrations
            )
            db.add(user)
            db.flush()
            # Audit trail
            db.add(PointRecord(
                user_id=user.user_id,
                resource_id=None,
                action_type="WELCOME_BONUS",
                points_delta=100,
                balance_after=100,
                created_at=now - timedelta(hours=60),
            ))
            db.commit()
            db.refresh(user)
            print(f"Created user {user.username} ({user.student_id}) with WELCOME_BONUS +100, id={user.user_id}")

        # Create tags pool
        all_tag_names = set()
        for r in SEED_RESOURCES:
            all_tag_names.update(r["tags"])
        tag_map = {}
        for tname in all_tag_names:
            existing_tag = db.query(Tag).filter(Tag.tag_name == tname).first()
            if existing_tag:
                tag_map[tname] = existing_tag
            else:
                tag = Tag(tag_name=tname, category="KEYWORD")
                db.add(tag)
                db.flush()
                tag_map[tname] = tag
        db.commit()

        # Create resources
        for i, r in enumerate(SEED_RESOURCES):
            existing_r = db.query(Resource).filter(Resource.title == r["title"]).first()
            if existing_r:
                print(f"  Resource '{r['title'][:40]}...' already exists, skipping")
                continue

            file_path = os.path.join(settings.STORAGE_DIR, r["file_name"])
            file_size = 0
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
            else:
                print(f"  ⚠️  File missing: {file_path} (will record path anyway)")

            res = Resource(
                title=r["title"],
                description=r["description"],
                file_path=file_path,
                file_type=r["file_type"],
                file_size=file_size,
                course_code=r["course_code"],
                academic_year=r["academic_year"],
                resource_type=r["resource_type"],
                status="PUBLISHED",
                avg_rating=None,        # 真实评分待用户提交
                download_count=0,       # 真实下载数从 0 累计
                uploader_id=user.user_id,
                pinned_until=(now + timedelta(days=7)) if r.get("pinned") else None,
                created_at=now - timedelta(hours=(9 - i) * 6),
            )
            db.add(res)
            db.flush()

            for tname in r["tags"]:
                db.add(ResourceTag(resource_id=res.resource_id, tag_id=tag_map[tname].tag_id))

            # Award upload points so leaderboard shows the user
            user.points_balance += 10
            db.add(PointRecord(
                user_id=user.user_id,
                resource_id=res.resource_id,
                action_type="UPLOAD_APPROVED",
                points_delta=10,
                balance_after=user.points_balance,
                created_at=now - timedelta(hours=(9 - i) * 6),
            ))
            user.upload_count += 1

            print(f"  Created resource: {r['title'][:50]}...")

        db.commit()
        print(f"\n✅ Seed complete. User {user.username} has {user.points_balance} pts, "
              f"{user.upload_count} uploads.")
        print(f"\nLogin credentials:")
        print(f"  Student ID: {SEED_USER['student_id']}")
        print(f"  Password:   {SEED_USER['password']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
