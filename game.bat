@echo off
REM 배치 파일이 위치한 폴더(프로젝트 루트)를 CWD로 설정합니다.
cd /d "%~dp0"

REM ⭐️ 1. pygame 폴더를 PYTHONPATH에 추가하여 main_game.py가 'countdown'을 찾도록 합니다.
set PYTHONPATH=%CD%\pygame;%PYTHONPATH%

REM ⭐️ 2. CWD를 'pygame' 폴더로 다시 설정하여 high_scores.txt 접근 문제를 해결합니다.
REM high_scores.txt는 pygame 폴더 안에 있으므로, CWD를 pygame으로 변경해야 합니다.
cd pygame

REM CWD(pygame 폴더)를 기준으로 main_game.py를 실행합니다.
REM (PYTHONPATH 덕분에 CWD 변경 후에도 모듈 임포트가 가능합니다.)
python main_game.py