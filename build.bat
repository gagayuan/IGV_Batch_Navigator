@echo off
chcp 65001 >nul

REM ============================================================
REM  自动计算当天版本号：V + YYMMDD（例如 20260630 → V260630）
REM ============================================================
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set VERSION=V%datetime:~2,6%

REM 生成 version.py 供 Python 代码 import
echo VERSION = "%VERSION%" > version.py

echo ========================================
echo   IGV 批量导航器 %VERSION% - 构建脚本
echo ========================================
echo.

@REM echo [1/3] 安装 PyInstaller...
@REM C:\Users\xuxi\ImJoyApp\miniconda3\python.exe -m pip install pyinstaller pillow requests -q -i https://pypi.tuna.tsinghua.edu.cn/simple
@REM if %errorlevel% neq 0 (
@REM     echo 安装失败，请检查 pip 是否可用。
@REM     pause
@REM     exit /b 1
@REM )
@REM echo 完成。
@REM echo.

@REM @REM echo [2/3] 生成图标...
@REM @REM C:\Users\xuxi\ImJoyApp\miniconda3\python.exe generate_icon.py
@REM @REM if %errorlevel% neq 0 (
@REM @REM     echo 图标生成失败，将使用默认图标继续构建。
@REM @REM )
@REM @REM echo.
echo [1/3] 清理上次构建残留...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "IGV_Batch_Navigator_*.spec" del /q "IGV_Batch_Navigator_*.spec"
echo 完成。
echo.

echo [2/3] 构建 exe (单文件/无控制台)...
C:\Users\xuxi\ImJoyApp\miniconda3\Scripts\pyinstaller.exe --onefile --windowed --icon=icon.ico --name="IGV_Batch_Navigator_%VERSION%" --hidden-import=requests --hidden-import=PyQt5.sip --hidden-import=sip ^
    --add-data="igv_core.py;." ^
    --add-data="tsv_csv_parser.py;." ^
    --add-data="settings_manager.py;." ^
    --add-data="settings_dialog.py;." ^
    --add-data="main_window.py;." ^
    --add-data="help_dialog.py;." ^
    --add-data="cmd_reference_dialog.py;." ^
    --add-data="log_dialog.py;." ^
    --add-data="i18n.py;." ^
    --add-data="icon.ico;." ^
    --add-data="version.py;." ^
    --add-data="igv_cmd.csv;." ^
    --add-data="igv_cmd_en.csv;." ^
    main.py

if %errorlevel% neq 0 (
    echo 构建失败！
    pause
    exit /b 1
)
echo.
echo ========================================
echo   构建完成！
echo   可执行文件: dist\IGV_Batch_Navigator_%VERSION%.exe
echo ========================================