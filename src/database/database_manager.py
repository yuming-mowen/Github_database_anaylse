"""数据入库入口模块。

该模块调用SOL语句，将对应关键词的相关数据入库到数据库中。
"""
import pymysql
import pandas as pd
import os

class GitHubDBManager:
    def __init__(self):
        # 数据库配置
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'database': 'github_analysis',
            'charset': 'utf8mb4'
        }

    def save_repos_to_db(self, repo_list, category):
        """将解析出的列表数据批量写入 repositories 和 repo_topics 表"""
        connection = pymysql.connect(**self.config)
        try:
            with connection.cursor() as cursor:
                for repo in repo_list:
                    # 基础字段提取
                    repo_id = repo.get("仓库ID")
                    if not repo_id: 
                        print(f"仓库名为：{repo.get("仓库名")} 的数据ID不明，入库失败！")
                        continue                     
                    name = str(repo.get("仓库名", "Unknown"))
                    stars = int(repo.get("星数", 0))
                    lang = str(repo.get("语言", "Unknown"))
                    description = str(repo.get("项目描述", ""))                    
                    # 转换日期：若格式非法则设为 None
                    updated_at_raw = repo.get("更新时间")
                    updated_at = updated_at_raw.replace('T', ' ').split('.')[0]
                    # 转换布尔值：确保传入 0 或 1 
                    is_sponsorable = 1 if repo.get("是否支持捐赠") else 0
                    has_issues = 1 if repo.get("是否有Issues") else 0                   
                    # 插入主表 
                    sql_repo = """REPLACE INTO repositories 
                                (repo_id, name, description, stars, language, category, updated_at, is_sponsorable, has_issues) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql_repo, (
                        repo_id, name, description, stars, lang, category, 
                        updated_at, is_sponsorable, has_issues
                    ))                    
                    # 插入标签表 
                    cursor.execute("DELETE FROM repo_topics WHERE repo_id = %s", (repo_id,))
                    for topic in repo.get("话题标签", []):
                        sql_topic = "INSERT INTO repo_topics (repo_id, topic_name) VALUES (%s, %s)"
                        cursor.execute(sql_topic, (repo_id, topic))
            
            # 提交所有操作
            connection.commit()
            print(f"成功入库 {len(repo_list)} 个项目。")
            
        except Exception as e:
            connection.rollback() # 出错则回滚，确保不存脏数据
            print(f"数据库操作失败: {e}")
        finally:
            connection.close()

def load_data_from_csv(csv_filepath):
    """从 CSV 文件加载数据，并转换为入库所需的字典列表格式

    Args:
        csv_filepath (str) - CSV 文件的路径
    Return:
        list - 格式化后的字典列表
    """
    try:
        # 使用 pandas 读取 CSV
        df = pd.read_csv(csv_filepath)
        
        # 将 DataFrame 转换为字典列表
        data_list = df.to_dict(orient='records')
        
        # 将 CSV 中合并的字符串标签恢复为列表
        for row in data_list:
            if '话题标签' in row and isinstance(row['话题标签'], str):
                # 如果标签不为空，用 split(',') 还原为列表
                row['话题标签'] = row['话题标签'].split(',') if row['话题标签'] else []
            else:
                row['话题标签'] = []
        print(f"成功从 {csv_filepath} 加载 {len(data_list)} 条数据。")
        return data_list
    except Exception as e:
        print(f"读取 CSV 失败: {e}")
        return []

def produce_all_data(path):
    """从路径中读取所有 .csv 文件并将数据全部入库

    Args:
        path - 入库数据存储相对路径
    """
    db = GitHubDBManager()
    data_files = [
            os.path.join(path, filename)
            for filename in os.listdir(path)
            if filename.endswith(".csv")
        ]
    for data_path in data_files:
        # 获取文件名
        filename = os.path.basename(data_path)
        #去掉后缀
        name_without_ext = os.path.splitext(filename)[0]
        # 去掉固定后缀 提取关键词
        keyword = name_without_ext.rsplit('_results', 1)[0]
        # 初始化 extracted_data
        extracted_data = load_data_from_csv(data_path)
        # 调用数据库管理器进行入库
        db.save_repos_to_db(extracted_data, keyword)
        print(f"关键词 {keyword} 相关数据成功导入！")
    
if __name__ == "__main__":
    path = "./data"
    produce_all_data(path)