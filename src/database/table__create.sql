/* * 数据库名称：github_analysis
 * 功能描述：用于存储 GitHub 机器人与 AI 相关项目的元数据及分类标签
 * 编码格式：utf8mb4 (支持存储 emoji 表情及多语言字符)
 */

-- 如果数据库不存在则创建，避免重复执行报错
CREATE DATABASE IF NOT EXISTS github_analysis CHARACTER SET utf8mb4;
USE github_analysis;

-- 创建仓库主表：存储每个 GitHub 项目的核心属性
CREATE TABLE repositories (
    repo_id INT PRIMARY KEY,             -- 唯一标识符，对应 GitHub 项目 ID
    name VARCHAR(255),                   -- 仓库名称
    description TEXT,                    -- 项目描述，使用 TEXT 类型存储长文本
    stars INT,                           -- 项目获星数，用于衡量热度
    language VARCHAR(50),                -- 主要编程语言
    updated_at DATETIME,                 -- 最近一次更新时间，用于趋势分析
    is_sponsorable BOOLEAN,              -- 是否支持捐赠/赞助
    has_issues BOOLEAN,                  -- 是否开启了问题反馈系统
    category VARCHAR(50)                 -- 分类字段，记录该项目由哪个关键词爬取所得
);

-- 创建标签表：用于存储项目的 Topics
CREATE TABLE repo_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,   -- 标签条目自增主键
    repo_id INT,                         -- 外键，关联 repositories 表的 repo_id
    topic_name VARCHAR(100),             -- 具体的标签名称
    
    -- 设置外键约束：当主表记录删除时，级联删除该项目的所有标签，保证数据一致性
    FOREIGN KEY (repo_id) REFERENCES repositories(repo_id) ON DELETE CASCADE
);