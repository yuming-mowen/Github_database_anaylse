# GitHub 开源项目趋势分析平台

## 项目介绍

本项目以 GitHub 搜索结果为数据源，构建了一个完整的开源项目分析平台。它结合爬虫、数据解析、MySQL 数据库和 Streamlit 可视化界面，旨在帮助你从技术标签、项目热度、语言分布、词云分析、质量矩阵到趋势演进，全面洞察 AI 和机器人领域开源项目的发展态势。

该工程适合用于：

- 开源数据采集与分析实践
- 技术趋势洞察与可视化展示
- 数据工程课程项目与报告展示
- GitHub 开源仓库分析与特征提取

## 主要功能

- GitHub 搜索结果HTML爬取
- GitHub搜索页面仓库信息提取与CSV输出
- 将 CSV 数据导入 MySQL 数据库
- 多维可视化分析：标签热度、Star 分布、语言市场、词云、质量矩阵、趋势热力图、关键词聚类
- Streamlit 交互分析平台

## 项目结构

```
data/                    # 存放关键词结果 CSV 文件
result_pictures/         # 可用于保存分析结果图片
src/
  config/
    config.py           # MySQL 数据库连接配置
  crawler/
    crawler.py          # GitHub 搜索结果爬虫模块
    extract.py          # HTML 提取并保存为 CSV
    produce_alldata.py  # 批量爬取关键词并生成 CSV
  data_analyse/         # 数据分析相关代码
    category_distribution.py
    keywords_catagory.py
    keywords_stars.py
    language_market.py
    quality_engagement.py
    stars_distribution.py
    trend_analysis.py
    wordcloud_engine.py
  data_base/
    table_create.sql     # 数据表创建脚本
    database_manager.py  # 数据自动入库脚本
    base_quary.sql       # 数据基础信息查询脚本
  data_platform/
    app.py               # Streamlit 可视化展示入口
```

## 依赖环境

建议使用 Python 3.8+。

安装依赖：

```bash
pip install requests fake_useragent beautifulsoup4 pandas pymysql streamlit matplotlib seaborn scikit-learn jieba wordcloud adjustText
```

## 数据库配置

默认数据库配置请查看 `src/config/config.py`：

```python
CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'github_analysis',
    'charset': 'utf8mb4'
}
```

如果你使用不同的 MySQL 账号或数据库名，请修改为实际配置。

## 初始化数据库

1. 启动 MySQL 服务
2. 执行 SQL 建表文件：

```bash
mysql -u root -p < src/data_base/table_create.sql
```

## 使用说明

### 1. 爬取 GitHub 数据并生成 CSV

```bash
cd src/crawler
python produce_alldata.py
```

该脚本会自动按关键词抓取 GitHub 搜索结果，并将提取结果保存为 `data/` 目录下的 CSV 文件。

### 2. 导入数据到 MySQL

```bash
cd src/data_base
python database_manager.py
```

该脚本会读取 `data/` 目录下的 CSV 文件，并将结果写入 `repositories` 和 `repo_topics` 表。

### 3. 启动可视化平台

```bash
cd src/data_platform
streamlit run app.py
```

打开浏览器访问 Streamlit 提供的本地地址，即可查看交互式分析页面。

## Streamlit 页面说明

- `数据管理平台`：显示仓库原始数据表
- `标签热度排行`：显示技术标签热度排名
- `星数分布分析`：展示 Star 数分布矩阵与密度图
- `语言市场份额`：展示编程语言占比饼图
- `项目描述词云`：展示描述词频词云
- `项目质量矩阵`：展示 Stars 与 Topics 关系
- `发展趋势分析`：展示年度热度演进热力图与趋势分类
- `关键词K聚类`：展示关键词聚类分析结果

## 代码说明

- `src/crawler/crawler.py`：爬取 GitHub 搜索结果 HTML
- `src/crawler/extract.py`：解析 HTML 并保存 CSV
- `src/crawler/produce_alldata.py`：批量爬取多个关键词并生成 CSV
- `src/data_base/database_manager.py`：CSV 数据解析与 MySQL 入库
- `src/data_analyse/`：各类数据分析与绘图模块
- `src/data_platform/app.py`：Streamlit 页面入口

## 备注

- `data/` 文件夹中已有 CSV 数据文件可直接用于分析
- 若爬虫触发 GitHub 反爬，可降低请求频率或使用网络代理
- 如需可视化图表保存功能，可将 `result_pictures/` 设为输出目录

---