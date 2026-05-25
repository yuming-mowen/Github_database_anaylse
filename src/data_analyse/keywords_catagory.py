"""
keywords_catagory.py
对各类别关键词进行聚类分析，使用平均 Stars、平均 Topics 和增长斜率作为聚类特征，并绘制聚类散点图。

说明：
- 通过线性回归计算类别增长斜率；
- 利用 KMeans 自定义实现进行类别聚类；
- 最终绘制各类别在影响力与增长潜力坐标系中的分布。
"""

import pandas as pd
import pymysql
from config import CONFIG
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text

# 全局设置中文字体和 seaborn 风格
plt.rcParams['font.sans-serif'] = ['SimHei']
sns.set_theme(style="whitegrid", font='SimHei')

def get_cluster_data():
    conn = pymysql.connect(**CONFIG)
    query = """
    SELECT r.category, r.stars, YEAR(r.updated_at) as year, 
           (SELECT COUNT(*) FROM repo_topics t WHERE t.repo_id = r.repo_id) as topics_count
    FROM repositories r
    WHERE r.updated_at IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # 计算每个类别的平均 Stars 和平均 Topics 数量
    stats = df.groupby('category').agg({
        'stars': 'mean',
        'topics_count': 'mean'
    })

    # 计算每个类别的增长斜率 (Slope)
    trend_data = df.groupby(['category', 'year']).size().reset_index(name='count')
    slopes = {}
    for cat in trend_data['category'].unique():
        subset = trend_data[trend_data['category'] == cat]
        if len(subset) > 2:
            model = LinearRegression()
            model.fit(subset[['year']], subset['count'])
            slopes[cat] = model.coef_[0]
        else:
            slopes[cat] = 0

    # 合并特征：构建 {category: [stars, topics, slope]}
    cluster_dict = {}
    for cat in stats.index:
        features = [
            stats.loc[cat, 'stars'], 
            stats.loc[cat, 'topics_count'], 
            slopes.get(cat, 0)
        ]
        cluster_dict[cat] = features
        
    return cluster_dict

def distance(x, y):
    """计算两个向量之间的欧氏距离。"""
    if len(x) == 0:
        return 0
    else:
        return np.sqrt(sum([(x[i] - y[i]) ** 2 for i in range(len(x))]))


def cal_center(lis, feature_num):
    """计算聚类中心，即所有特征向量的均值。"""
    result = [0 for _ in range(feature_num)]
    if len(lis) == 0:
        return result
    else:
        for feature in lis:
            for i in range(feature_num):
                result[i] += feature[i]
        return [r / len(lis) for r in result]

def KMeans(feature_dict, category_num):
    """自定义 KMeans 聚类实现，将类别特征分为指定数量的聚类。"""
    features = []
    labels = []
    for k, v in feature_dict.items():
        labels.append(k)
        features.append(v)
    # 使用前 category_num 个样本初始化中心
    centers = []
    for i in range(category_num):
        centers.append(features[i])
    # 最大训练1000轮次
    for epoh in range(1000):  
        category = [[] for _ in range(category_num)]
        # 开始计算每一个数据属于哪一类
        for feature in features:
            dis = [distance(feature, center) for center in centers]
            category[dis.index(min(dis))].append(feature)
        # 更新新的中心
        new_centers = []
        for f in category:
            feature_num = len(features[0])
            new_centers.append(cal_center(f, feature_num))
        if sum([distance(x, y) for x, y in zip(new_centers, centers)]) < 1e-6:
            break
        else:
            for i, center in enumerate(new_centers):
                centers[i] = center
    # 最终分类：将每个特征向量映射回对应的类别名称
    key_word = [[] for _ in range(category_num)]
    for i, c in enumerate(category):
        for f in c:
            value = f
            for k, v in feature_dict.items():
                if v == value:
                    keys = k
                    break
            key_word[i].append(keys)
    return key_word

def plot_cluster_scatter(feature_dict, key_word):
    """
    feature_dict: {category: [stars, topics, slope]}
    key_word: [[cat1, cat2], [cat3, cat4], ...]
    """
    plt.rcParams['font.sans-serif'] = ['SimHei']
    sns.set_theme(style="whitegrid", font='SimHei')
    plt.figure(figsize=(10, 6))
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    
    # 提取所有特征以便计算坐标范围
    all_features = np.array(list(feature_dict.values()))
    
    # 用于存储需要调整的文本对象
    texts_to_adjust = []
    
    # 遍历每个聚类组进行绘图
    for i, cluster_cats in enumerate(key_word):
        # 获取当前类别的所有特征向量
        cluster_features = np.array([feature_dict[cat] for cat in cluster_cats if cat in feature_dict])
        
        if len(cluster_features) > 0:
            # 取 Stars (影响力, 索引0) 为 x 轴，Slope (增长潜力, 索引2) 为 y 轴
            plt.scatter(cluster_features[:, 0], cluster_features[:, 2], 
                        c=colors[i % len(colors)], label=f'Cluster {i}', s=100, alpha=0.6)
            
            # 创建文本对象，但不立即显示
            for j, cat in enumerate(cluster_cats):
                # 创建文本，暂时存入列表
                t = plt.text(feature_dict[cat][0], feature_dict[cat][2], cat, fontsize=9)
                texts_to_adjust.append(t)
    
    plt.xlabel('Average Stars (影响力)', fontsize=12)
    plt.ylabel('Growth Slope (增长潜力)', fontsize=12)
    plt.title('关键词聚类分布图', fontsize=14)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    adjust_text(texts_to_adjust, 
                arrowprops=dict(arrowstyle='->', color='gray', lw=0.5), # 自动添加指引线
                only_move={'text': 'y'}, # 优先在 Y 轴方向（垂直方向）拉开
                expand_points=(1.5, 1.5)) # 增加文本与散点之间的保护距离
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    feature_dict = get_cluster_data()
    # print("--- 关键词特征字典 ---")
    # for k, v in feature_dict.items():
    #     print(f"{k}: {v}")
    key_word = KMeans(feature_dict, 3)
    plot_cluster_scatter(feature_dict, key_word)