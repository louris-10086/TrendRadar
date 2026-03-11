@echo off
chcp 65001 >nul
cd /d "D:\插件\TrendRadar-master"
"D:\shark\study word\python.exe" github_rss_gen.py
"D:\shark\study word\python.exe" -m trendradar
