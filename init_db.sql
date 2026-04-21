-- init_db.sql
-- 创建图书管理系统数据库
-- 用法: mysql -uroot -p123456 < init_db.sql

CREATE DATABASE IF NOT EXISTS `library`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
