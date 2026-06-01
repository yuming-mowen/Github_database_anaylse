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
from data_analyse.category_distribution import plot_top_topics
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
label_list = ["数据管理平台", "标签热度排行"]
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