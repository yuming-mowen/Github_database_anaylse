"""
统计并绘制最常见的技术标签（topics）的出现频率（前 20 名）。
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
from config import CONFIG

# 建立数据库连接并查询出现频率最高的 20 个标签
conn = pymysql.connect(**CONFIG)
query = """
SELECT topic_name, COUNT(*) as frequency 
FROM repo_topics 
GROUP BY topic_name 
ORDER BY frequency DESC 
LIMIT 20
"""
df = pd.read_sql(query, conn)

# 可视化设置（中文字体 + seaborn 风格）
plt.rcParams['font.sans-serif'] = ['SimHei']
sns.set_theme(style="whitegrid", font='SimHei')

# 绘制水平条形图，便于显示较长的标签名称
plt.figure(figsize=(10, 8))
sns.barplot(data=df, x='frequency', y='topic_name', palette='magma')

plt.title("开源项目中出现频率最高的 20 个技术标签", fontsize=16)
plt.xlabel("出现频率 (项目数)", fontsize=12)
plt.ylabel("标签名称", fontsize=12)

plt.tight_layout()
plt.show()
