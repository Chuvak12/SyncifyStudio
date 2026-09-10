@echo off
chcp 65001 > nul
echo ===================================================
echo   1. Очистка старых кэшей и процессов...
echo ===================================================
taskkill /F /IM SyncifyStudio.exe > nul 2>&1
rd /s /q build > nul 2>&1
rd /s /q dist > nul 2>&1

echo ===================================================
echo   2. Сборка приложения SyncifyStudio.exe...
echo ===================================================

if exist "icon.ico" (
    echo [i] Найдена иконка icon.ico, вшиваем...
    pyinstaller --noconsole --onefile --icon="icon.ico" --name="SyncifyStudio" --collect-all ytmusicapi --collect-all webview --collect-all pystray app.py
) else (
    echo [!] Файл icon.ico не найден! Собираем со стандартной иконкой...
    pyinstaller --noconsole --onefile --name="SyncifyStudio" --collect-all ytmusicapi --collect-all webview --collect-all pystray app.py
)

if exist dist\SyncifyStudio.exe (
    move /y dist\SyncifyStudio.exe .\
    echo ===================================================
    echo   ГОТОВО! Приложение успешно собрано.
    echo ===================================================
) else (
    echo ===================================================
    echo   ОШИБКА: Сборка не удалась.
    echo ===================================================
)
pause