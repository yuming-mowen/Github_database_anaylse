"""数据处理入口模块。

该模块调用爬虫获取 GitHub 搜索结果 HTML，然后提取仓库信息并保存为对应关键词的 CSV 文件。
"""

import os

import crawler
import extract


def data_produce(keywords):
    """对多个关键词执行爬取、提取和 CSV 保存流程。

    Args:
        keywords (list[str]): 需要抓取的关键词列表。
    """
    for keyword in keywords:
        github_crawler = crawler.GitHubCrawler()
        github_crawler.run(keyword=keyword, pages=5)

        extracted_results = []
        data_directory = "./data"
        html_files = [
            os.path.join(data_directory, filename)
            for filename in os.listdir(data_directory)
            if filename.endswith(".html")
        ]

        for html_path in html_files:
            repo_data = extract.extract_repo_data(html_path)
            if repo_data:
                extracted_results.extend(repo_data)
            os.remove(html_path)

        if extracted_results:
            output_filename = f"{keyword}_results.csv"
            extract.save_to_csv(extracted_results, save_dir=data_directory, filename=output_filename)
        else:
            print(f"警告: 关键词 {keyword} 未提取到有效数据")


if __name__ == "__main__":
    keywords = [
        "robotics", "slam", "quadruped", "motion-planning", "kinematics",
        "computer-vision", "optimization", "path-planning", "graph-neural-networks", "control-theory",
        "reinforcement-learning", "supervised-learning", "unsupervised-learning", "time-series", "feature-engineering",
        "large-language-model", "diffusion-model", "transformer", "multimodal", "nlp"
    ]
    data_produce(keywords)

        