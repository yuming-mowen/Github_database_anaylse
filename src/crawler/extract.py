"""HTML 内容提取与 CSV 保存模块。

该模块用于解析 GitHub 搜索结果页面中的仓库数据，并将其保存为 CSV 文件。
"""

import json
import os

import pandas as pd
from bs4 import BeautifulSoup


def extract_repo_data(html_file_path):
    """解析单个 HTML 文件，提取仓库信息列表。"""
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    script_tag = soup.find("script", {"data-target": "react-app.embeddedData"})
    if not script_tag or not script_tag.string:
        print(f"未找到目标数据标签: {html_file_path}")
        return []

    data = json.loads(script_tag.string)
    repos = data.get("payload", {}).get("results", [])

    extracted_list = []
    for repo in repos:
        extracted_item = {
            "仓库名": repo.get("hl_name"),
            "星数": repo.get("followers"),
            "语言": repo.get("language"),
            "更新时间": repo.get("repo", {}).get("repository", {}).get("updated_at"),
            "项目描述": repo.get("hl_trunc_description"),
            "话题标签": repo.get("topics", []),
            "是否支持捐赠": repo.get("sponsorable"),
            "是否有Issues": repo.get("repo", {}).get("repository", {}).get("has_issues"),
            "仓库ID": repo.get("id"),
            "类型": repo.get("type")
        }
        extracted_list.append(extracted_item)

    return extracted_list

def save_to_csv(data_list, save_dir, filename="github_results.csv"):
    """将提取结果保存为 CSV 文件。

    Args:
        data_list (list[dict]): 提取后的仓库信息列表。
        save_dir (str): CSV 文件保存目录。
        filename (str): 输出 CSV 文件名。
    """
    if not data_list:
        print("没有数据可保存。")
        return

    df = pd.DataFrame(data_list)
    if "话题标签" in df.columns:
        df["话题标签"] = df["话题标签"].apply(lambda x: ",".join(x) if isinstance(x, list) else x)

    os.makedirs(save_dir, exist_ok=True)
    output_path = os.path.join(save_dir, filename)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"数据已成功保存至: {output_path}")

# 执行并打印结果
if __name__ == "__main__":
    html_path = "./data/github_page_1.html"
    extracted_results = extract_repo_data(html_path)
    for item in extracted_results:
        print(item)
    save_to_csv(extracted_results, save_dir="./data", filename="github_results.csv")