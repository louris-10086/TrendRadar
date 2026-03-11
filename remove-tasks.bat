@echo off
chcp 65001 >nul
echo 正在删除 TrendRadar 定时任务...
schtasks /delete /tn "TrendRadar_0800" /f >nul 2>&1 && echo ✅ 已删除 08:00 任务 || echo ⚠️ 08:00 任务不存在
schtasks /delete /tn "TrendRadar_1200" /f >nul 2>&1 && echo ✅ 已删除 12:00 任务 || echo ⚠️ 12:00 任务不存在
schtasks /delete /tn "TrendRadar_2000" /f >nul 2>&1 && echo ✅ 已删除 20:00 任务 || echo ⚠️ 20:00 任务不存在
echo.
echo 所有定时任务已清除
pause
