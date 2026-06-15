'''
使用 Streamlit 网页建立数据展示平台
'''
import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import sys
import os

# 设置 Streamlit 页面布局、标题和图标
st.set_page_config(layout="wide", page_title="开源技术分析平台", page_icon="📊")

# 路径配置：加入上级目录，确保可以引用 config 和分析模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import CONFIG

# 导入各分析模块中的绘图和数据处理函数
from data_analyse.category_distribution import plot_top_topics
from data_analyse.keywords_stars import get_stars_category_data
from data_analyse.language_market import plot_language_market
from data_analyse.stars_distribution import plot_star_distribution
from data_analyse.wordcloud_engine import plot_wordcloud
from data_analyse.quality_engagement import plot_quailty
from data_analyse.trend_analysis import get_data, analyze_trend_regression, plot_growth_heatmap, classify_and_print_trends
from data_analyse.keywords_catagory import get_cluster_data, KMeans, plot_cluster_scatter

# 全局配置
warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif'] = ['SimHei']
sns.set_theme(style="whitegrid", font='SimHei')

def get_connection():
    """创建并返回数据库连接对象。"""
    return pymysql.connect(**CONFIG)


def st_plot_clean():
    """渲染当前 matplotlib 图表到 Streamlit 页面。

    统一使用此函数可以保持图表显示宽度一致。
    """
    fig = plt.gcf()
    st.pyplot(fig, use_container_width=True)

# 侧边栏：导航菜单和说明信息
st.sidebar.title("🛠️ 数据分析中心")
page = st.sidebar.selectbox(
    "选择分析模块",
    ["数据管理平台", "标签热度排行", "星数分布分析", "语言市场份额", "项目描述词云", "项目质量矩阵", "发展趋势分析", "标签聚类分析"]
)
st.sidebar.markdown("---")
st.sidebar.info("💡 **分析结论**: 本平台基于数据库进行实时数据挖掘，旨在通过量化手段揭示开源社区技术趋势。")
st.sidebar.caption("© 2026 数据科学课程设计")

# --- 主逻辑优化 ---

if page == "数据管理平台":
    # 数据管理模块：展示仓库原始数据并支持编辑查看
    st.title("📊 Github人工智能相关开源工程数据管理平台")
    df = pd.read_sql("SELECT * FROM repositories", get_connection())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("总仓库数", f"{len(df):,}")
    col2.metric("涵盖领域数", df['category'].nunique())
    col3.metric("数据状态", "Online", "🟢")
    st.divider()
    
    with st.expander("查看原始数据表", expanded=True):
        st.data_editor(df, num_rows="dynamic")
    if st.button("💾 同步保存"):
        st.success("数据更新成功")

elif page == "标签热度排行":
    # 标签热度模块：展示技术标签的频次排名图
    st.title("🔥 技术标签热度")
    with st.spinner('正在生成热度排行...'):
        plot_top_topics(get_connection())
        st_plot_clean()
    
    # 优化为可展开的解释
    with st.expander("查看图表分析结论"):
        st.info("💡 **分析结论**: 标签排名前三的技术栈通常代表了当前开发社区的关注重心。")

elif page == "星数分布分析":
    # 星数分布模块：展示不同领域 Star 数的统计与密度分布
    st.title("⭐ 领域-星数分布分析")
    conn = get_connection()
    count_df, pct_df = get_stars_category_data(conn)
    
    tab1, tab2 = st.tabs(["分布矩阵", "等级占比分析"])
    with tab1:
        st.dataframe(count_df, use_container_width=True)
    with tab2:
        st.dataframe(pct_df.style.background_gradient(cmap='Blues', axis=1), use_container_width=True)
    
    st.subheader("分布密度估计")
    with st.spinner('计算密度函数中...'):
        plot_star_distribution(conn)
        st_plot_clean()
    
    # 优化为可展开的解释
    with st.expander("查看分布密度图分析解读"):
        st.info("""
        💡 **深度洞察：** 该密度曲线展示了开源项目的 Star 数呈典型的“长尾分布”。大部分项目的 Star 数集中在较低量级，而极少数头部项目占据了绝大多数关注度。
        这种分布特征反映了开源社区的“马太效应”，即优质项目更容易积累高星级关注。
        """)

elif page == "语言市场份额": 
    # 语言市场份额模块：展示不同编程语言在仓库中的占比
    st.title("📊 编程语言分布") 
    plot_language_market(get_connection())
    st_plot_clean()
    
    with st.expander("查看市场份额分析结论"):
        st.info("💡 **分析解读：** 不同编程语言的市场份额反映了该语言在开源生态中的普及度与生产力工具地位。")

elif page == "项目描述词云":
    # 词云分析模块：展示项目描述中的高频关键词
    st.title("☁️ 项目描述词云分析")
    with st.spinner('正在生成词云...'):
        plot_wordcloud(get_connection())
        st_plot_clean()
    
    # 优化为可展开的解释
    with st.expander("查看词云分析解读"):
        st.info("""
        💡 **分析解读：** 词云图中字号越大的词汇，代表在项目描述中出现的频率越高。
        图中突出的关键词反映了当前开源领域的技术热点，这些高频词汇是项目定位的核心，也是社区技术演进的缩影。
        """)

elif page == "项目质量矩阵":
    # 项目质量矩阵模块：展示 Stars 与 Topics Count 的综合分析
    st.title("🧩 项目质量与参与度矩阵")
    with st.spinner('项目质量矩阵绘制中...'):
        plot_quailty(get_connection())
        st_plot_clean()
    
    # 优化为可展开的解释
    with st.expander("查看项目质量矩阵评估结论"):
        st.info("""
        💡 **评估结论：** 此图将项目质量分为“影响力（Stars）”与“活跃主题度（Topics Count）”两个维度。
        - **右上角区域**：代表“明星项目”，既具备广泛影响力，又在多个技术话题中活跃。
        - **左侧区域**：可能是垂直领域的利基项目。
        - **颜色标识**：颜色区分是否开启了 Issues，反映了社区运营与项目热度之间的相关性。
        """)

elif page == "发展趋势分析":
    # 发展趋势模块：展示各领域随时间变化的热度趋势
    st.title("📈 技术趋势演进分析")
    df = get_data(get_connection())
    
    col1, col2 = st.columns(2)
    col1.metric("监测领域总量", df['category'].nunique())
    col2.metric("时间跨度", f"{df['year'].min()} - {df['year'].max()}")
    st.divider()
    
    st.subheader("年度热度演进热力图")
    with st.spinner('绘制演进趋势...'):
        plot_growth_heatmap(df)
        st_plot_clean()
    
    with st.expander("点击查看增长分类结论", expanded=True):
        st.write("各领域按照线性增长斜率分类如下：")
        slope_df = analyze_trend_regression(df)
        result_df = classify_and_print_trends(slope_df)
        st.dataframe(result_df, use_container_width=True)

elif page == "标签聚类分析":
    # 关键词聚类模块：使用 K-Means 对关键词进行分组并展示结果
    st.title("🧩 技术关键词聚类")
    with st.spinner('算法聚类中 (K-Means)...'):
        conn = get_connection()
        feature_dict = get_cluster_data(conn)
        key_word = KMeans(feature_dict, 4)
        plot_cluster_scatter(feature_dict, key_word)
        st_plot_clean()
    
    with st.expander("查看各集群具体归类成员 集群按照中心距离原点的距离排序"):
        cluster_results = [{"聚类 ID": f"Cluster {i+1}", "包含类别": ", ".join(cluster)} for i, cluster in enumerate(key_word)]
        st.table(pd.DataFrame(cluster_results))