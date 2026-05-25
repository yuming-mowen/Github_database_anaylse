/* * 数据库名称：github_analysis
 * 功能描述：用于对该数据库中储存的信息进行初步统计与分析
 */

USE github_analysis;
-- 删除表中所有信息 用于调试代码
SET SQL_SAFE_UPDATES = 0;
TRUNCATE TABLE repo_topics;
TRUNCATE TABLE repositories;
SET SQL_SAFE_UPDATES = 1;

-- 打印表中现有所有信息
SELECT * FROM repositories;
SELECT * FROM repo_topics;

-- 查看仓库总量
SELECT COUNT(*) AS total_repositories FROM repositories;
-- 查看标签总量
SELECT COUNT(*) AS total_topics FROM repo_topics;

-- 领域分布分析
SELECT category, COUNT(*) AS count 
FROM repositories 
GROUP BY category 
ORDER BY count DESC;

-- 热度排行
SELECT name, stars, language, category 
FROM repositories 
ORDER BY stars DESC;

-- 编程语言统计
SELECT language, COUNT(*) AS project_count 
FROM repositories 
GROUP BY language;

-- 标签聚合分析
SELECT topic_name, COUNT(*) AS frequency 
FROM repo_topics 
GROUP BY topic_name 
ORDER BY frequency DESC 
LIMIT 20;

-- 多表联合查询 验证关联性
SELECT r.name, t.topic_name 
FROM repositories r 
JOIN repo_topics t ON r.repo_id = t.repo_id 
WHERE r.stars > 10000;

