"""
分析并绘制仓库 Star 数的分布密度图（使用核密度估计，KDE）。
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import numpy as np
from config import CONFIG

# 建立数据库连接并查询有星数的仓库（排除 stars <= 0）
conn = pymysql.connect(**CONFIG)
query = "SELECT stars FROM repositories WHERE stars > 0"
df = pd.read_sql(query, conn)

# 设置中文字体与 seaborn 风格
plt.rcParams['font.sans-serif'] = ['SimHei']
sns.set_theme(style="whitegrid", font='SimHei')

# 绘图：对数尺度下的核密度估计（KDE）
plt.figure(figsize=(10, 6))

# 对 stars 做 log10 变换以压缩数量级差异，避免被极大值主导
sns.kdeplot(data=np.log10(df['stars']), fill=True, color="teal", alpha=0.3)

plt.title("开源项目 Star 数分布密度 (Log-scale Distribution)", fontsize=16)
plt.xlabel("Log(Stars)", fontsize=12)
plt.ylabel("Density (密度)", fontsize=12)

# 将 x 轴刻度标注为实际的星数量级（10^x）
plt.xticks([0, 1, 2, 3, 4], ['1', '10', '100', '1000', '10000'])

plt.tight_layout()
plt.show()
