@echo off
REM 배치 파일이 위치한 폴더(루트 폴더)를 현재 작업 디렉토리(CWD)로 설정합니다.
cd /d "%~dp0"

REM CWD를 기준으로 pygame 폴더 안의 main_game.py를 실행합니다.
python testserver\test_setver.py