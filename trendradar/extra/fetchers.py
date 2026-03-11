# coding=utf-8
"""
额外数据获取模块

获取实时天气、金价、GitHub 无人机项目、微博热搜等额外信息
"""

import time
from typing import Dict, List, Optional


def fetch_weather(city: str = "珠海金湾区") -> str:
    """
    获取城市实时天气（使用 wttr.in，无需 API Key）

    Returns:
        str: 格式化的天气信息，失败时返回错误提示
    """
    try:
        import requests

        url = f"https://wttr.in/{city}?format=j1"
        headers = {"User-Agent": "TrendRadar/1.0 (weather-bot)"}
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        data = response.json()

        current = data.get("current_condition", [{}])[0]

        # 天气描述（中文优先，否则英文）
        lang_zh = current.get("lang_zh", [])
        desc = lang_zh[0].get("value", "") if lang_zh else current.get("weatherDesc", [{}])[0].get("value", "未知")

        temp_c = current.get("temp_C", "?")
        feels_like = current.get("FeelsLikeC", "?")
        humidity = current.get("humidity", "?")
        wind_speed = current.get("windspeedKmph", "?")

        lines = [
            f"{desc}  {temp_c}°C（体感 {feels_like}°C）",
            f"湿度 {humidity}%  风速 {wind_speed} km/h",
        ]

        # 近 3 天预报
        forecast_parts = []
        for day in data.get("weather", [])[:3]:
            date = day.get("date", "")[5:]  # 只显示 MM-DD
            max_t = day.get("maxtempC", "?")
            min_t = day.get("mintempC", "?")
            hourly = day.get("hourly", [])
            day_desc = ""
            if hourly:
                mid = hourly[len(hourly) // 2]
                zh = mid.get("lang_zh", [])
                day_desc = zh[0].get("value", "") if zh else ""
            forecast_parts.append(f"{date} {day_desc} {min_t}~{max_t}°C")

        if forecast_parts:
            lines.append("近3日: " + " | ".join(forecast_parts))

        return "\n".join(lines)

    except Exception as e:
        return f"天气获取失败（{e}）"


def fetch_gold_prices() -> str:
    """
    获取黄金/白银价格

    数据来源：
    - 国际金价：goldprice.org（CNY/克）
    - 主要金店参考价（国际价 + 行业惯例加价）
    - 银行金条参考价

    Returns:
        str: 格式化的金价信息
    """
    try:
        import requests

        lines = []

        # 从 goldprice.org 获取 CNY 金银价（盎司）
        url = "https://data-asg.goldprice.org/dbXRates/CNY"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://goldprice.org/",
            "Origin": "https://goldprice.org",
        }
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        data = r.json()

        items = data.get("items", [])
        if not items:
            return "金价数据暂时无法获取"

        item = items[0]
        xau_oz = item.get("xauPrice", 0)   # CNY/盎司
        xag_oz = item.get("xagPrice", 0)   # CNY/盎司
        TROY_OZ_TO_G = 31.1035

        xau_g = round(xau_oz / TROY_OZ_TO_G, 2) if xau_oz else 0
        xag_g = round(xag_oz / TROY_OZ_TO_G, 2) if xag_oz else 0

        if xau_g:
            lines.append(f"国际金价：{xau_g} 元/克")

            # 主要金店（零售足金，通常加 30~60 元工费）
            ctf = round(xau_g + 45, 0)    # 周大福
            lao = round(xau_g + 40, 0)    # 老凤祥
            chng = round(xau_g + 38, 0)   # 中国黄金
            pd = round(xau_g + 50, 0)     # 周生生

            lines.append(f"\n各大金店参考价（足金 Au999，含工费估算）：")
            lines.append(f"  周大福 约 {int(ctf)} 元/克")
            lines.append(f"  老凤祥 约 {int(lao)} 元/克")
            lines.append(f"  中国黄金 约 {int(chng)} 元/克")
            lines.append(f"  周生生 约 {int(pd)} 元/克")

            # 银行金条（Au9999，通常加 5~15 元）
            bank = round(xau_g + 8, 2)
            lines.append(f"\n银行金条参考价（Au9999）：约 {bank} 元/克")
            lines.append("（以上为估算值，实际价以各店官网为准）")

        if xag_g:
            lines.append(f"\n国际银价：{xag_g} 元/克")

        return "\n".join(lines) if lines else "金价数据解析失败"

    except Exception as e:
        return f"金价获取失败（{e}）"


def fetch_github_drone(limit: int = 5) -> str:
    """
    获取 GitHub 无人机相关热门开源项目（无需 Token，限速 10 次/分钟）

    Returns:
        str: 格式化的项目列表
    """
    try:
        import requests

        url = "https://api.github.com/search/repositories"
        params = {
            "q": "drone OR UAV OR quadcopter OR autopilot",
            "sort": "stars",
            "order": "desc",
            "per_page": limit,
        }
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TrendRadar/1.0",
        }
        r = requests.get(url, params=params, headers=headers, timeout=12)
        r.raise_for_status()
        items = r.json().get("items", [])

        if not items:
            return "暂无数据"

        lines = []
        for item in items:
            name = item.get("full_name", "")
            desc = item.get("description") or "（无描述）"
            stars = item.get("stargazers_count", 0)
            lang = item.get("language") or ""
            updated = (item.get("updated_at") or "")[:10]

            # 截断描述
            if len(desc) > 50:
                desc = desc[:47] + "..."

            star_str = f"{stars // 1000}k" if stars >= 1000 else str(stars)
            line = f"⭐{star_str}  {name}"
            if lang:
                line += f"  [{lang}]"
            line += f"\n      {desc}"
            if updated:
                line += f"  ({updated})"
            lines.append(line)

        return "\n".join(lines)

    except Exception as e:
        return f"GitHub 数据获取失败（{e}）"


def fetch_weibo_hot(current_results: Optional[Dict] = None, limit: int = 15) -> str:
    """
    从已抓取的 current_results 中提取微博实时热搜

    Args:
        current_results: 爬虫抓取的结果字典，结构为 {platform_id: {title: {...}}}
        limit: 最多显示条数

    Returns:
        str: 格式化的微博热搜列表，未找到时返回空字符串
    """
    if not current_results:
        return ""

    # 微博平台可能的 ID
    weibo_ids = {"weibo", "weibo-hot", "weibo_hot"}
    weibo_data = None
    for pid in weibo_ids:
        if pid in current_results:
            weibo_data = current_results[pid]
            break

    if not weibo_data:
        return ""

    # 按最低排名排序（排名越小越靠前）
    items = []
    for title, info in weibo_data.items():
        if isinstance(info, dict):
            ranks = info.get("ranks", [])
            min_rank = min(ranks) if ranks else 999
            items.append((min_rank, title))

    items.sort(key=lambda x: x[0])

    lines = []
    for i, (rank, title) in enumerate(items[:limit], 1):
        lines.append(f"{i}. {title}")

    return "\n".join(lines)


def fetch_all_extra_data(current_results: Optional[Dict] = None) -> Dict:
    """
    获取所有额外数据

    Args:
        current_results: 当前爬取结果，用于提取微博热搜

    Returns:
        dict: {
            "weather": str,
            "gold": str,
            "github_drone": str,
            "weibo": str,
        }
    """
    print("[额外数据] 正在获取实时数据（天气/金价/GitHub/微博）...")

    weather = fetch_weather("珠海金湾区")
    print("[额外数据] ✓ 天气")

    gold = fetch_gold_prices()
    print("[额外数据] ✓ 金价")

    github = fetch_github_drone(limit=5)
    print("[额外数据] ✓ GitHub 无人机项目")

    weibo = fetch_weibo_hot(current_results, limit=15)
    if weibo:
        print("[额外数据] ✓ 微博热搜")
    else:
        print("[额外数据] ℹ 微博数据未找到（平台未启用或未抓取到）")

    return {
        "weather": weather,
        "gold": gold,
        "github_drone": github,
        "weibo": weibo,
    }
