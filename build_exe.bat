pyinstaller --noconfirm ^
    --log-level=WARN ^
    --onefile ^
    --nowindow ^
    --add-data="src\sprites;sprites" ^
    --name MAZEGAME ^
    --icon=src\sprites\logo_32x32.ico ^
    src\main.py

pause

