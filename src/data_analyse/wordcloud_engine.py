"""
从数据库中读取项目描述并生成关键词云图，包含中文注释和文本清洗流程。
"""

import pymysql
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from config import CONFIG
import seaborn as sns
import re
import string

# 数据库提取：读取所有非空 description 字段
conn = pymysql.connect(**CONFIG)
query = "SELECT description FROM repositories WHERE description IS NOT NULL"
cursor = conn.cursor()
cursor.execute(query)
results = cursor.fetchall()
conn.close()

# 图表样式配置：使用中文字体并启用 seaborn 风格
plt.rcParams['font.serif'] = ['Times New Roman']
sns.set_theme(style="whitegrid", font='SimHei')

# 文本清洗与拼接
# 将查询结果中的元组转换为纯字符串列表，并过滤掉过短的描述
text_list = [row[0] for row in results if len(row[0]) > 5]
all_text = " ".join(text_list)

# 移除 HTML 标签，避免词云中出现无意义的标签文本
clean_html_text = re.sub(r'<[^>]+>', ' ', all_text)

# 分词：使用 jieba 对中文文本进行切分
words = jieba.cut(clean_html_text)
clean_text = " ".join(words)

# 生成词云：设置字体、背景和停用词过滤
single_letters = set(string.ascii_lowercase)
stop_words = {'em', 'the', 'is', 'in', 'to', 'of', 'and', 'for', 'from', 'this', 'an',  'on', 'with', "的"}

wc = WordCloud(
    font_path='C:/Windows/Fonts/simhei.ttf',
    background_color='black',
    width=1200,
    height=800,
    max_words=100,
    colormap='viridis',
    stopwords=stop_words | single_letters
)

wc.generate(clean_text)

# 可视化展示词云图
plt.figure(figsize=(10, 6))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.title("项目描述关键词云图", fontsize=16)
plt.tight_layout()
plt.show()
