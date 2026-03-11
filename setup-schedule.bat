@echo off
chcp 65001 >nul
setlocal

echo ==========================================
echo   TrendRadar 定时推送注册（每日3次）
echo   08:00 / 12:00 / 20:00
echo ==========================================
echo.

set "BAT_PATH=D:\插件\TrendRadar-master\run.bat"
set "TASK_PREFIX=TrendRadar"

echo 正在删除旧任务（如有）...
schtasks /delete /tn "%TASK_PREFIX%_0800" /f >nul 2>&1
schtasks /delete /tn "%TASK_PREFIX%_1200" /f >nul 2>&1
schtasks /delete /tn "%TASK_PREFIX%_2000" /f >nul 2>&1

echo 正在创建任务：早上 08:00 ...
schtasks /create /tn "%TASK_PREFIX%_0800" ^
  /tr "\"%BAT_PATH%\"" ^
  /sc DAILY /st 08:00 ^
  /rl HIGHEST /f >nul
if %errorlevel% neq 0 (
    echo ❌ 08:00 任务创建失败
) else (
    echo ✅ 08:00 任务已创建
)

echo 正在创建任务：中午 12:00 ...
schtasks /create /tn "%TASK_PREFIX%_1200" ^
  /tr "\"%BAT_PATH%\"" ^
  /sc DAILY /st 12:00 ^
  /rl HIGHEST /f >nul
if %errorlevel% neq 0 (
    echo ❌ 12:00 任务创建失败
) else (
    echo ✅ 12:00 任务已创建
)

echo 正在创建任务：晚上 20:00 ...
schtasks /create /tn "%TASK_PREFIX%_2000" ^
  /tr "\"%BAT_PATH%\"" ^
  /sc DAILY /st 20:00 ^
  /rl HIGHEST /f >nul
if %errorlevel% neq 0 (
    echo ❌ 20:00 任务创建失败
) else (
    echo ✅ 20:00 任务已创建
)

echo.
echo ==========================================
echo 已注册的 TrendRadar 定时任务：
echo ==========================================
schtasks /query /tn "%TASK_PREFIX%_0800" /fo list 2>nul | findstr /i "TaskName Status"
schtasks /query /tn "%TASK_PREFIX%_1200" /fo list 2>nul | findstr /i "TaskName Status"
schtasks /query /tn "%TASK_PREFIX%_2000" /fo list 2>nul | findstr /i "TaskName Status"

echo.
echo 完成！可在「任务计划程序」中查看 TrendRadar_* 任务
echo 如需取消：双击本脚本目录下的 remove-tasks.bat
echo.
pause
