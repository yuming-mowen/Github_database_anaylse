import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import sys
import os

# 设置页面布局
st.set_page_config(layout="wide", page_title="开源技术分析平台")

# 全局配置
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入绘图源文件
from data_analyse.category_distribution import plot_top_topics
from data_analyse.keywords_stars import get_stars_category_data
from data_analyse.language_market import plot_language_market
from data_analyse.stars_distribution import plot_star_distribution
from data_analyse.wordcloud_engine import plot_wordcloud
from data_analyse.quality_engagement import plot_quailty
from data_analyse.trend_analysis import get_data, analyze_trend_regression, plot_growth_heatmap, classify_and_print_trends
from data_analyse.keywords_catagory import get_cluster_data, KMeans, plot_cluster_scatter
from config.config import CONFIG


def st_plot_clean():
    # 自动获取当前所有活动的 plt 图表
    fig = plt.gcf()
    # 强制将 fig 传入，Streamlit 就会识别为规范调用，从而隐藏那个警告框
    st.pyplot(fig)

warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif'] = ['SimHei']
sns.set_theme(style="whitegrid", font='SimHei')

def get_connection():
    return pymysql.connect(**CONFIG)

# 侧边栏导航
label_list = ["数据管理平台", "标签热度排行", "星数分布分析", "语言市场份额", 
              "项目描述词云", "项目质量矩阵", "发展趋势分析", "关键词K聚类"]
st.sidebar.title("🛠️ 数据分析中心")
page = st.sidebar.selectbox("选择分析模块", label_list)

# 主逻辑 
if page == "数据管理平台":
    st.title("📊 开源数据管理平台")
    df = pd.read_sql("SELECT * FROM repositories", get_connection())
    edited_df = st.data_editor(df, num_rows="dynamic")
    if st.button("保存更改"):
        st.info("数据已更新")
    
    col1, col2 = st.columns(2)
    col1.metric("总仓库数", len(df))
    col2.metric("涵盖领域数", df['category'].nunique())

elif page == "标签热度排行":
    st.title("🔥 技术标签热度")
    # 传入连接函数，调用绘图函数
    conn = get_connection()
    fig = plot_top_topics(conn)
    st_plot_clean()

elif page == "星数分布分析":
    st.title("⭐ 领域-星数分布分析")
    conn = get_connection()
    count_df, pct_df = get_stars_category_data(conn)
    
    st.subheader("分布数量矩阵")
    # 使用 dataframe 展示，支持用户点击列名进行排序
    st.dataframe(count_df, use_container_width=True)
    
    st.subheader("各领域等级占比 (%)")
    # 使用 st.dataframe 的样式化功能 (Styler)，突出显示数值
    st.dataframe(
        pct_df.style.background_gradient(cmap='Blues', axis=1), 
        use_container_width=True
    )

    st.subheader("分布密度分布")
    fig = plot_star_distribution(conn)
    st_plot_clean()


elif page == "语言市场份额":
    st.title("📊 编程语言分布")
    conn = get_connection()
    fig = plot_language_market(conn)
    st_plot_clean()

elif page == "项目描述词云":
    st.title("☁️ 项目描述词云分析")
    conn = get_connection()
    fig = plot_wordcloud(conn)
    st_plot_clean()

elif page == "项目质量矩阵":
    st.title("🧩 项目质量与参与度矩阵")
    conn = get_connection()
    fig = plot_quailty(conn)
    st_plot_clean()

elif page == "发展趋势分析":
    st.title("📈 技术趋势演进分析")
    conn = get_connection()
    df = get_data(conn) # 假设你已定义好该函数
    
    # 拟合与分类计算
    slope_df = analyze_trend_regression(df)
    result_df = classify_and_print_trends(slope_df)
    
    # 上方展示热力图
    st.subheader("年度热度演进热力图")
    fig = plot_growth_heatmap(df)
    st_plot_clean()
    
    # 下方展示分类结果表格
    st.subheader("趋势转折点分类结果")
    st.dataframe(result_df, use_container_width=True)

elif page == "关键词K聚类":
    st.title("🧩 技术关键词聚类")
    conn = get_connection()
    feature_dict = get_cluster_data(conn)
    key_word = KMeans(feature_dict, 4)
    
    # 绘图展示
    fig = plot_cluster_scatter(feature_dict, key_word)
    st_plot_clean()
    
    # 将聚类结果整理成表格展示
    st.subheader("聚类成员详细列表")
    cluster_results = []
    for i, cluster in enumerate(key_word):
        cluster_results.append({"聚类 ID": f"Cluster {i+1}", "包含类别": ", ".join(cluster)})
    
    st.table(pd.DataFrame(cluster_results))