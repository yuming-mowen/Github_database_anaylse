"""
绘制项目质量/参与度评估矩阵：以仓库 `stars`（影响力）为 x 轴，`topics_count`（关注度/话题数量）为 y 轴，使用颜色区分是否开启 Issues。
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
from config import CONFIG

# 建立数据库连接并查询需要的字段：stars、该仓库的话题数量（topics_count）和是否开启 issues
conn = pymysql.connect(**CONFIG)
query = """
SELECT r.stars, COUNT(t.topic_name) as topics_count, r.has_issues
FROM repositories r
LEFT JOIN repo_topics t ON r.repo_id = t.repo_id
GROUP BY r.repo_id
"""
df = pd.read_sql(query, conn)

# 绘图样式设置（中文字体 + seaborn 白底网格）
plt.rcParams['font.sans-serif'] = ['SimHei']
sns.set_theme(style="whitegrid", font='SimHei')
plt.figure(figsize=(10, 7))

# 绘制散点图：
# - x: stars（后面使用对数坐标显示）
# - y: topics_count（仓库话题/标签数量，代表活跃主题或关注点）
# - hue/style: has_issues（是否开启 issues，布尔或标识字段）
scatter = sns.scatterplot(
    data=df,
    x='stars',
    y='topics_count',
    hue='has_issues',
    style='has_issues',
    palette='viridis',
    alpha=0.7,
    s=80
)

# 因为 stars 分布通常跨越多个数量级，使用对数坐标更易观察趋势和簇
plt.xscale('log')

plt.title("开源项目质量评估矩阵 (Quality/Engagement Matrix)", fontsize=16)
plt.xlabel("Stars (对数比例)", fontsize=12)
plt.ylabel("Topics Count (标签数量)", fontsize=12)
plt.legend(title='Has Issues')

plt.tight_layout()
plt.show()