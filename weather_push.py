"""
天气信息推送脚本
获取城市实时天气，推送到飞书
"""

import requests
import json
import urllib3
from datetime import datetime

urllib3.disable_warnings()

# ===================== 配置区 =====================
CITY = "珠海"              # 城市名称（支持中文或英文）
FEISHU_WEBHOOK = "https://www.feishu.cn/flow/api/trigger-webhook/0c66295817138d83ccff8980c7c8b328"
# ==================================================

WIND_DIR_MAP = {
    'N': '北风', 'NNE': '北偏东风', 'NE': '东北风', 'ENE': '东偏北风',
    'E': '东风', 'ESE': '东偏南风', 'SE': '东南风', 'SSE': '南偏东风',
    'S': '南风', 'SSW': '南偏西风', 'SW': '西南风', 'WSW': '西偏南风',
    'W': '西风', 'WNW': '西偏北风', 'NW': '西北风', 'NNW': '北偏西风',
}

WEATHER_EMOJI = {
    'Sunny': '☀️', 'Clear': '🌙', 'Partly cloudy': '⛅', 'Cloudy': '☁️',
    'Overcast': '☁️', 'Mist': '🌫️', 'Fog': '🌫️', 'Rain': '🌧️',
    'Drizzle': '🌦️', 'Snow': '❄️', 'Sleet': '🌨️', 'Thunder': '⛈️',
    'Blizzard': '🌨️', 'Blowing snow': '🌨️', 'Light rain': '🌦️',
    'Heavy rain': '🌧️', 'Moderate rain': '🌧️', 'Light snow': '🌨️',
    '晴天': '☀️', '多云': '⛅', '阴天': '☁️', '小雨': '🌦️',
    '中雨': '🌧️', '大雨': '🌧️', '雾': '🌫️', '雪': '❄️',
}


def get_weather(city: str) -> dict:
    """从 wttr.in 获取天气数据"""
    url = f"https://wttr.in/{city}?format=j1&lang=zh"
    r = requests.get(url, timeout=15, verify=False,
                     headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    r.raise_for_status()
    return r.json()


def format_weather(city: str, data: dict) -> str:
    """格式化天气信息为飞书消息文本"""
    cc = data["current_condition"][0]

    temp = cc["temp_C"]
    feels_like = cc["FeelsLikeC"]
    humidity = cc["humidity"]
    wind_speed = cc["windspeedKmph"]
    wind_dir = cc.get("winddir16Point", "")
    visibility = cc["visibility"]
    pressure = cc["pressure"]
    uv_index = cc.get("uvIndex", "N/A")

    # 天气描述（优先中文）
    desc_zh = ""
    lang_list = cc.get("lang_zh", [])
    if lang_list:
        desc_zh = lang_list[0].get("value", "")
    if not desc_zh:
        desc_zh = cc.get("weatherDesc", [{}])[0].get("value", "未知")

    # 获取 emoji
    emoji = "🌤️"
    for key, val in WEATHER_EMOJI.items():
        if key.lower() in desc_zh.lower():
            emoji = val
            break

    wind_dir_zh = WIND_DIR_MAP.get(wind_dir, f"{wind_dir}风")

    # 今明后三天预报
    forecast_lines = []
    for day in data.get("weather", [])[:3]:
        date_str = day.get("date", "")
        max_c = day.get("maxtempC", "?")
        min_c = day.get("mintempC", "?")
        hourly = day.get("hourly", [{}])
        day_desc = ""
        for h in hourly:
            lang = h.get("lang_zh", [])
            if lang:
                day_desc = lang[0].get("value", "")
                break
        if not day_desc:
            day_desc = hourly[0].get("weatherDesc", [{}])[0].get("value", "") if hourly else ""

        # 日期格式
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            wd = weekdays[dt.weekday()]
            date_label = f"{dt.month}/{dt.day} {wd}"
        except Exception:
            date_label = date_str

        forecast_lines.append(f"  {date_label}   {min_c}~{max_c}°C   {day_desc}")

    forecast_text = "\n".join(forecast_lines)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    msg = f"""📍 {city} 实时天气

{emoji} {desc_zh}   {temp}°C（体感 {feels_like}°C）
💧 湿度: {humidity}%
🌬️ {wind_dir_zh} {wind_speed} km/h
👁️ 能见度: {visibility} km
🌡️ 气压: {pressure} hPa
☀️ 紫外线指数: {uv_index}

📅 近三日预报
{forecast_text}

⏰ 更新时间: {now}"""

    return msg


def push_feishu(webhook_url: str, title: str, content: str) -> bool:
    """推送消息到飞书"""
    payload = {
        "title": title,
        "content": content,
    }
    r = requests.post(
        webhook_url,
        json=payload,
        timeout=15,
        verify=False,
        headers={"Content-Type": "application/json"},
    )
    return r.status_code == 200


def main():
    print(f"正在获取 {CITY} 天气...")
    try:
        data = get_weather(CITY)
    except Exception as e:
        print(f"❌ 天气获取失败: {e}")
        return

    msg = format_weather(CITY, data)
    print(msg)
    print("\n正在推送到飞书...")

    success = push_feishu(FEISHU_WEBHOOK, f"📍 {CITY} 实时天气", msg)
    if success:
        print("✅ 推送成功！")
    else:
        print("❌ 推送失败，请检查 Webhook 地址")


if __name__ == "__main__":
    main()
