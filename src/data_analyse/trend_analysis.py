"""
分析各类别在不同年份中的热度趋势，基于线性回归计算增长斜率，并可视化年度热度热力图。

功能：
- 从数据库读取类别、更新时间和话题数量等信息；
- 对不同类别的年度出现次数进行线性回归，计算增长斜率；
- 绘制年度热度演进热力图；
- 根据斜率对趋势类别进行简单分类。
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pymysql
from config import CONFIG

# 设置中文字体和 seaborn 风格，使图表在中文环境下显示正确
plt.rcParams['font.sans-serif'] = ['SimHei']
sns.set_theme(style="whitegrid", font='SimHei')

def analyze_trend_regression(df):
    """机器学习拟合趋势：计算各领域的增长斜率。"""
    trend_data = df.groupby(['category', 'year']).size().reset_index(name='count')
    results = []
    for cat in trend_data['category'].unique():
        subset = trend_data[trend_data['category'] == cat]
        if len(subset) > 2:
            model = LinearRegression()
            model.fit(subset[['year']], subset['count'])
            results.append({'category': cat, 'slope': model.coef_[0]})
    return pd.DataFrame(results)

def plot_growth_heatmap(df):
    """增长率热力图：可视化年度热度演进。"""
    trend_data = df.groupby(['category', 'year']).size().reset_index(name='count')
    heatmap_data = trend_data.pivot(index='category', columns='year', values='count').fillna(0)
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlGnBu')
    plt.title("各领域关键词年度热度演进热力图", fontsize=14)
    plt.tight_layout()
    plt.show()

def classify_and_print_trends(slope_df):
    """转折点分析：基于斜率对趋势进行分类并打印结果。"""
    bins = [-float('inf'), 0, 0.5, float('inf')]
    labels = ['衰减型', '平稳存量型', '高速增长型']
    slope_df['trend_type'] = pd.cut(slope_df['slope'], bins=bins, labels=labels)
    
    print("\n--- 趋势转折点分类分析结果 ---")
    print(slope_df.sort_values('slope', ascending=False))
    return slope_df

def get_data():
    conn = pymysql.connect(**CONFIG)
    # 联表获取类别、星数、年份信息
    query = """
    SELECT r.category, r.stars, YEAR(r.updated_at) as year, 
           (SELECT COUNT(*) FROM repo_topics t WHERE t.repo_id = r.repo_id) as topics_count
    FROM repositories r
    WHERE r.updated_at IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    df = get_data()
    # 拟合计算
    slope_df = analyze_trend_regression(df)
    # 热力图
    plot_growth_heatmap(df)
    # 分类打印
    classify_and_print_trends(slope_df)