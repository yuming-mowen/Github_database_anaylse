"""GitHub 搜索结果爬虫模块。

该模块通过 GitHub 搜索页面获取仓库搜索结果 HTML，并保存到本地文件。
"""

import os
import random
import time

import requests
from fake_useragent import UserAgent


class GitHubCrawler:
    """用于抓取 GitHub 仓库搜索结果 HTML 的爬虫。"""

    def __init__(self):
        self.base_url = "https://github.com/search"
        self.user_agent = UserAgent()
        self.session = requests.Session()

    def get_headers(self):
        """生成随机 HTTP 请求头，模拟浏览器请求。"""
        return {
            "User-Agent": self.user_agent.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive"
        }

    def fetch_page(self, keyword, page_num):
        """获取指定搜索关键字和页码的 GitHub 搜索结果页面。

        Args:
            keyword (str): 搜索关键字。
            page_num (int): 页码。

        Returns:
            str | None: 成功返回 HTML 文本，失败返回 None。
        """
        try:
            params = {
                'q': keyword,
                'type': 'repositories',
                'p': page_num
            }
            response = self.session.get(self.base_url, headers=self.get_headers(), params=params, timeout=10)
            if response.status_code == 200:
                return response.text
            print(f"Failed to fetch page {page_num}, status: {response.status_code}")
            return None
        except Exception as exc:
            print(f"Error occurred while fetching page {page_num}: {exc}")
            return None

    def run(self, keyword, pages=3):
        """按页抓取 GitHub 搜索结果并保存到本地 HTML 文件。"""
        for page_index in range(pages):
            page_num = page_index + 1
            retry_required = True
            while retry_required:
                print(f"正在抓取 GitHub 关键词 '{keyword}' 第 {page_num} 页...")
                html_content = self.fetch_page(keyword, page_num)
                if html_content:
                    self.save_raw_html(html_content, page_num)
                    retry_required = False
                else:
                    print("触发反爬，停止脚本等待 1 分钟...")
                    time.sleep(60)

            time.sleep(random.uniform(3, 6))

    def save_raw_html(self, html_content, page_num):
        """将抓取到的 HTML 内容保存到本地 data 目录。"""
        save_dir = "./data"
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"github_page_{page_num}.html")
        with open(file_path, "w", encoding="utf-8") as output_file:
            output_file.write(html_content)
        print(f"页面已保存至 {file_path}")

if __name__ == "__main__":
    crawler = GitHubCrawler()
    # 机器人相关项目
    crawler.run(keyword="robotics", pages=3)