"""
GitHub 搜索结果 → 本地 RSS 文件
在 TrendRadar 运行前先执行，把搜索结果写成 RSS 文件供 TrendRadar 读取
"""

import requests
import json
import os
import urllib3
from datetime import datetime, timezone
from xml.sax.saxutils import escape

urllib3.disable_warnings()

# ===================== 配置区 =====================
SEARCHES = [
    {
        "id": "github-uav-search",
        "query": "无人机",
        "description": "GitHub 无人机仓库（按最近更新）",
        "per_page": 5,
        "sort": "updated",
        "order": "desc",
    },
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
# ==================================================


def fetch_repos(query: str, sort: str, order: str, per_page: int) -> list:
    url = "https://api.github.com/search/repositories"
    params = {"q": query, "sort": sort, "order": order, "per_page": per_page}
    headers = {
        "User-Agent": "TrendRadar/1.0",
        "Accept": "application/vnd.github.v3+json",
    }
    r = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
    r.raise_for_status()
    return r.json().get("items", [])


def repos_to_rss(title: str, description: str, repos: list) -> str:
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for repo in repos:
        updated = repo.get("updated_at", "")[:10]
        stars = repo.get("stargazers_count", 0)
        desc = repo.get("description") or ""
        lang = repo.get("language") or "未知"
        item_desc = f"⭐{stars} | {lang} | 更新:{updated} | {escape(desc)}"
        items.append(f"""  <item>
    <title><![CDATA[{repo['full_name']}]]></title>
    <link>{repo['html_url']}</link>
    <description><![CDATA[{item_desc}]]></description>
    <pubDate>{now}</pubDate>
    <guid>{repo['html_url']}</guid>
  </item>""")

    items_xml = "\n".join(items)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title><![CDATA[{title}]]></title>
    <link>https://github.com/search?q={requests.utils.quote(title)}&amp;type=repositories&amp;s=updated&amp;o=desc</link>
    <description><![CDATA[{description}]]></description>
    <lastBuildDate>{now}</lastBuildDate>
{items_xml}
  </channel>
</rss>"""


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for cfg in SEARCHES:
        print(f"正在获取 GitHub 搜索: {cfg['query']} ...")
        try:
            repos = fetch_repos(cfg["query"], cfg["sort"], cfg["order"], cfg["per_page"])
            rss = repos_to_rss(cfg["description"], cfg["description"], repos)
            out_path = os.path.join(OUTPUT_DIR, f"{cfg['id']}.xml")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(rss)
            print(f"[OK] {len(repos)} repos -> {out_path}")
        except Exception as e:
            print(f"[FAIL] {e}")


if __name__ == "__main__":
    main()
