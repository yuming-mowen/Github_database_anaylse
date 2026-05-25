"""
对开源项目的编程语言分布进行统计并绘制饼图。
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
from config import CONFIG

# 建立数据库连接（使用 config 中的连接参数）
conn = pymysql.connect(**CONFIG)

# 查询：按编程语言统计仓库数量，按数量降序排列
query = "SELECT language, COUNT(*) as count FROM repositories GROUP BY language ORDER BY count DESC"
df = pd.read_sql(query, conn)

# 数据预处理：计算占比并将小众语言合并为 "Other"
total = df['count'].sum()
df['percentage'] = df['count'] / total

# 将占比小于 threshold 的语言视为小众并合并
threshold = 0.02
others = df[df['percentage'] < threshold].copy()
main_df = df[df['percentage'] >= threshold].copy()

if not others.empty:
    # 将小众语言的数量合并为一行 "Other"
    new_row = pd.DataFrame({'language': ['Other'], 'count': [others['count'].sum()]})
    main_df = pd.concat([main_df, new_row], ignore_index=True)

# 绘图：设置中文字体和图形大小
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.figure(figsize=(10, 7))

# 使用 seaborn 的调色板绘制饼图
colors = sns.color_palette('pastel')[0:len(main_df)]
plt.pie(
    main_df['count'],
    labels=main_df['language'],
    autopct='%1.1f%%',
    colors=colors,
    startangle=140,
    explode=[0.05] * len(main_df)  # 轻微分离每个扇区以增强可读性
)

plt.title("开源项目编程语言市场份额分布", fontsize=16)
plt.axis('equal')  # 保证饼图是圆的
plt.tight_layout()
plt.show()
