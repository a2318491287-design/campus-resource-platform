-- ================================================================
-- Campus Academic Resource Sharing Platform
-- MySQL / MariaDB Database Schema  ·  v1.0  ·  May 2, 2026
-- ================================================================
-- This is the canonical SQL DDL referenced in SDD v1.0 §8.2.
-- The FastAPI backend creates the same schema via SQLAlchemy ORM,
-- but this file is provided for direct DBA inspection and audit.
-- ================================================================

CREATE DATABASE IF NOT EXISTS campus_resource_platform
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE campus_resource_platform;

-- ----------------------------------------------------------------
-- users
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  user_id          INT          NOT NULL AUTO_INCREMENT,
  student_id       VARCHAR(20)  NOT NULL UNIQUE,
  username         VARCHAR(50)  NOT NULL,
  password_hash    VARCHAR(255) NOT NULL,
  email            VARCHAR(100) NOT NULL UNIQUE,
  points_balance   INT          NOT NULL DEFAULT 100
                                CHECK (points_balance >= 0),
  upload_count     INT          NOT NULL DEFAULT 0,
  download_credits INT          NOT NULL DEFAULT 3,
  is_admin         TINYINT(1)   NOT NULL DEFAULT 0,
  created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  INDEX idx_student_id (student_id),
  INDEX idx_email (email)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------
-- resources
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resources (
  resource_id      INT          NOT NULL AUTO_INCREMENT,
  title            VARCHAR(200) NOT NULL,
  description      TEXT,
  file_path        VARCHAR(500) NOT NULL,
  file_type        ENUM('PDF','DOCX','PPTX','IMAGE','OTHER') NOT NULL,
  file_size        BIGINT       NOT NULL,
  course_code      VARCHAR(20)  NOT NULL,
  academic_year    INT          NOT NULL,
  resource_type    ENUM('NOTES','PAST_PAPER','ASSIGNMENT','LECTURE','GUIDE','OTHER') NOT NULL,
  status           ENUM('PENDING','PUBLISHED','REJECTED','REMOVED')
                                NOT NULL DEFAULT 'PENDING',
  avg_rating       DECIMAL(3,2) DEFAULT NULL,
  download_count   INT          NOT NULL DEFAULT 0,
  uploader_id      INT          NOT NULL,
  rejection_reason VARCHAR(500) DEFAULT NULL,
  pinned_until     DATETIME     DEFAULT NULL,
  created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (resource_id),
  FOREIGN KEY (uploader_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FULLTEXT INDEX ft_search (title, description),
  INDEX idx_course_code (course_code),
  INDEX idx_status (status),
  INDEX idx_academic_year (academic_year)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------
-- tags
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tags (
  tag_id    INT          NOT NULL AUTO_INCREMENT,
  tag_name  VARCHAR(50)  NOT NULL UNIQUE,
  category  ENUM('COURSE','TYPE','KEYWORD') NOT NULL,
  PRIMARY KEY (tag_id),
  INDEX idx_category (category)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------
-- resource_tags
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resource_tags (
  resource_id INT NOT NULL,
  tag_id      INT NOT NULL,
  PRIMARY KEY (resource_id, tag_id),
  FOREIGN KEY (resource_id) REFERENCES resources(resource_id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id)      REFERENCES tags(tag_id)           ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------
-- ratings
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ratings (
  rating_id   INT       NOT NULL AUTO_INCREMENT,
  resource_id INT       NOT NULL,
  user_id     INT       NOT NULL,
  stars       TINYINT   NOT NULL CHECK (stars BETWEEN 1 AND 5),
  comment     TEXT,
  created_at  DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (rating_id),
  UNIQUE KEY uq_user_resource_rating (user_id, resource_id),
  FOREIGN KEY (resource_id) REFERENCES resources(resource_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id)     REFERENCES users(user_id)         ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------
-- point_records
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS point_records (
  record_id     INT     NOT NULL AUTO_INCREMENT,
  user_id       INT     NOT NULL,
  resource_id   INT     DEFAULT NULL,
  action_type   ENUM('UPLOAD_APPROVED','DOWNLOAD_RECEIVED',
                     'RATING_RECEIVED','SPEND_DOWNLOAD',
                     'REDEEM_DOWNLOAD_CREDIT','REDEEM_PIN',
                     'FREE_DOWNLOAD','WELCOME_BONUS') NOT NULL,
  points_delta  INT      NOT NULL,
  balance_after INT      NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (record_id),
  FOREIGN KEY (user_id)     REFERENCES users(user_id)         ON DELETE CASCADE,
  FOREIGN KEY (resource_id) REFERENCES resources(resource_id) ON DELETE SET NULL,
  INDEX idx_user_id (user_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------
-- downloads
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS downloads (
  download_id   INT      NOT NULL AUTO_INCREMENT,
  resource_id   INT      NOT NULL,
  user_id       INT      NOT NULL,
  downloaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (download_id),
  FOREIGN KEY (resource_id) REFERENCES resources(resource_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id)     REFERENCES users(user_id)         ON DELETE CASCADE,
  INDEX idx_resource_id (resource_id),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------
-- redemptions
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS redemptions (
  redemption_id INT      NOT NULL AUTO_INCREMENT,
  user_id       INT      NOT NULL,
  reward_type   ENUM('DOWNLOAD_CREDIT','PIN') NOT NULL,
  points_cost   INT      NOT NULL,
  resource_id   INT      DEFAULT NULL,
  activated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at    DATETIME DEFAULT NULL,
  PRIMARY KEY (redemption_id),
  FOREIGN KEY (user_id)     REFERENCES users(user_id)         ON DELETE CASCADE,
  FOREIGN KEY (resource_id) REFERENCES resources(resource_id) ON DELETE SET NULL
) ENGINE=InnoDB;
