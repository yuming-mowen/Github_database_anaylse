"""
绘制关键词与仓库 Star 数的分布多索引表格。
"""

import pandas as pd
import pymysql
from config import CONFIG

conn = pymysql.connect(**CONFIG)

# 获取类别与星数数据
query = "SELECT category, stars FROM repositories"
df = pd.read_sql(query, conn)

# 定义星数分桶区间 (0-10, 10-100, 100-1000, 1000-10000, 10000+)
bins = [0, 10, 100, 1000, 10000, float('inf')]
labels = ['0-10', '10-100', '100-1000', '1000-10000', '10000+']
df['star_range'] = pd.cut(df['stars'], bins=bins, labels=labels, right=False)

# 构建多索引矩阵
multi_index_table = df.pivot_table(
    index=['category'], 
    columns=['star_range'], 
    aggfunc='size', 
    fill_value=0
)

print("--- 关键词领域-星数分布矩阵 ---")
print(multi_index_table)

# 计算占比百分比
pct_table = multi_index_table.div(multi_index_table.sum(axis=1), axis=0) * 100
print("\n--- 各领域热度等级分布百分比 (%) ---")
print(pct_table.round(1))
