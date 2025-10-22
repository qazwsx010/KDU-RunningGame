import pygame
import sys
import time
import os
import random 
import config_utils 

# network_client, result_scene, countdown 모듈이 있다고 가정합니다.
from network_client import setup_client_socket, get_player_data, get_client_socket, close_client_socket
from result_scene import ResultScene 
import countdown 

pygame.init()

# ----------------- 💡 화면 및 트랙 크기 설정 -----------------
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size() 
FPS = 60

# 트랙 기하학 설정
y_ai = SCREEN_HEIGHT * 0.25 
y_player = SCREEN_HEIGHT * 0.75 
LINE_THICKNESS = 3
start_x = SCREEN_WIDTH * 0.05 
end_x = SCREEN_WIDTH * 0.95 

# 상수 가져오기
BOX_SIZE = config_utils.BOX_SIZE
box_center_offset = config_utils.box_center_offset
AI_SPEED = config_utils.AI_SPEED
PLAYER_SPEED_CORRECTION = config_utils.PLAYER_SPEED_CORRECTION

# ----------------- 게임 상태 및 초기화 변수 -----------------

INITIAL_BOX_POS = {'ai': start_x, 'player': start_x}
LAST_APPLIED_SPEED = 0.0 
clock = pygame.time.Clock()

current_scene = None 
small_font = pygame.font.Font(None, 48) 

# ----------------- 에셋 초기화 (config_utils에서 로드) -----------------

print("에셋 초기화 중: config_utils.py를 통해 로드 시도...")

config_utils.init_assets(ai_size=BOX_SIZE)

print(f"로드된 AI 프레임 수: {len(config_utils.ai_frames)}")
print(f"로드된 Player 프레임 수: {len(config_utils.player_frames)}")


if get_client_socket() is None:
    setup_client_socket()

last_reconnect_attempt_time = 0.0
RECONNECT_COOLDOWN = 1.0 
PLAYER_FRAME_DURATION_MS = config_utils.AI_FRAME_DURATION_MS 

# ----------------- 게임 핵심 함수 -----------------

def draw_track():
    """트랙, 결승선 및 배경을 그립니다."""
    screen.fill(config_utils.WHITE) 
    pygame.draw.line(screen, config_utils.RED, (end_x, 0), (end_x, SCREEN_HEIGHT), LINE_THICKNESS + 2) 
    pygame.draw.line(screen, config_utils.BLACK, (start_x, y_ai), (end_x, y_ai), LINE_THICKNESS)
    pygame.draw.line(screen, config_utils.BLACK, (start_x, y_player), (end_x, y_player), LINE_THICKNESS)

def reset_game():
    """게임 상태를 초기 상태로 되돌리고 카운트다운을 시작합니다."""
    global current_scene, box_pos, LAST_APPLIED_SPEED, start_time, player_finish_time, last_reconnect_attempt_time
    
    current_scene = None
    box_pos = INITIAL_BOX_POS.copy() 
    player_finish_time = None

    last_reconnect_attempt_time = 0.0 
    setup_client_socket() 
    
    print("--- 게임이 초기화되었습니다. 서버 데이터 수신 대기 중... ---")
    draw_track()
    loading_font = pygame.font.Font(None, 80)
    loading_text_surface = loading_font.render("서버 데이터 동기화 중...", True, (50, 50, 50))
    screen.blit(loading_text_surface, loading_text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
    pygame.display.flip()
    
    max_wait_attempts = 50 
    wait_delay = 0.2       
    received_valid_speed = False
    
    for attempt in range(max_wait_attempts):
        pygame.event.pump() 
        client_socket = get_client_socket()
        
        if client_socket is None:
            setup_client_socket()
            client_socket = get_client_socket() 
            if client_socket is None:
                time.sleep(wait_delay)
                continue
        
        server_data = get_player_data()
        
        if get_client_socket() is None:
            time.sleep(wait_delay)
            continue

        if server_data and 'speed' in server_data:
            raw_speed = server_data['speed']
            if raw_speed > 0.00:
                global LAST_APPLIED_SPEED
                LAST_APPLIED_SPEED = raw_speed * PLAYER_SPEED_CORRECTION 
                received_valid_speed = True
                break
        
        time.sleep(wait_delay) 

    if received_valid_speed:
        print(f"--- ✅ 데이터 동기화 성공! 초기 속도: {LAST_APPLIED_SPEED:.2f} (총 {attempt+1}회 시도) ---")
    else:
        LAST_APPLIED_SPEED = 0.0
        print(f"--- ⚠️ 데이터 동기화 실패 (유효 속도 미수신). 게임 시작! ---")
        
    start_time = countdown.run_countdown_scene(screen, draw_track) 

def move_ai(current_x):
    new_x = current_x + AI_SPEED
    if new_x + BOX_SIZE >= end_x: 
        new_x = end_x - BOX_SIZE 
        return new_x
    return new_x

def move_player_with_network(current_x):
    global LAST_APPLIED_SPEED, last_reconnect_attempt_time
    
    client_socket = get_client_socket()
    
    if client_socket is None:
        current_time = time.time()
        if current_time - last_reconnect_attempt_time > RECONNECT_COOLDOWN:
            setup_client_socket() 
            last_reconnect_attempt_time = current_time
        return current_x 
    
    server_data = get_player_data()
    current_player_speed = LAST_APPLIED_SPEED 

    if server_data and 'speed' in server_data:
        raw_speed = server_data['speed']
        if raw_speed > 0.00: 
             current_player_speed = raw_speed * PLAYER_SPEED_CORRECTION
             LAST_APPLIED_SPEED = current_player_speed 
        else:
             current_player_speed = 0.0 
             
    else:
        current_player_speed = 0.0 

    new_x = current_x + current_player_speed 
    if new_x + BOX_SIZE >= end_x:
        new_x = end_x - BOX_SIZE 
        return new_x
    return new_x

# ----------------- 메인 게임 루프 -----------------

start_time = countdown.run_countdown_scene(screen, draw_track) 
box_pos = INITIAL_BOX_POS.copy() 

running = True
player_finish_time = None
winner = None

if start_time is None:
    running = False

ai_current_frame_idx = 0
ai_last_switch_ms = pygame.time.get_ticks()

player_current_frame_idx = 0
player_last_switch_ms = pygame.time.get_ticks()

while running:
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    if current_scene is not None:
        current_scene.process_input(events)
        current_scene.render(screen)
        
        if not current_scene.is_running:
            reset_game()
            
    else:
        # 1. AI 및 플레이어 움직임
        box_pos['ai'] = move_ai(box_pos['ai'])
        box_pos['player'] = move_player_with_network(box_pos['player'])
        
        # 2. 애니메이션 프레임 업데이트 로직
        now_ms = pygame.time.get_ticks()
        frame_duration = config_utils.AI_FRAME_DURATION_MS
        
        # AI 애니메이션
        if len(config_utils.ai_frames) > 0 and now_ms - ai_last_switch_ms >= frame_duration:
            ai_current_frame_idx = (ai_current_frame_idx + 1) % len(config_utils.ai_frames)
            ai_last_switch_ms = now_ms

        # 플레이어 애니메이션
        if len(config_utils.player_frames) > 0 and now_ms - player_last_switch_ms >= PLAYER_FRAME_DURATION_MS:
            player_current_frame_idx = (player_current_frame_idx + 1) % len(config_utils.player_frames)
            player_last_switch_ms = now_ms

        # 3. 게임 종료 확인
        game_over_by_ai = box_pos['ai'] >= end_x - BOX_SIZE
        game_over_by_player = box_pos['player'] >= end_x - BOX_SIZE
        
        if game_over_by_ai or game_over_by_player:
            
            if game_over_by_player:
                winner = "PLAYER"
                player_finish_time = time.time() - start_time
            else:
                winner = "AI"
                player_finish_time = 99999.0 
            
            is_win = (winner == "PLAYER")
            screen_size_tuple = (SCREEN_WIDTH, SCREEN_HEIGHT)
            
            current_scene = ResultScene(
                screen_size=screen_size_tuple, 
                time_record=player_finish_time, 
                is_win=is_win
            )

        # 4. 게임 화면 그리기
        draw_track() 
        
        # AI 프레임 그리기
        ai_surf = config_utils.ai_frames[ai_current_frame_idx] if len(config_utils.ai_frames) > 0 else config_utils.ai_image
        screen.blit(ai_surf, (box_pos['ai'], y_ai - box_center_offset))
        
        # 플레이어 프레임 그리기
        player_surf = config_utils.player_frames[player_current_frame_idx] if len(config_utils.player_frames) > 0 else config_utils.player_image
        screen.blit(player_surf, (box_pos['player'], y_player - box_center_offset))
        
        # 시간 표시
        current_time = time.time() - start_time
        time_text_display = f"TIME: {current_time:.2f}s"
        time_text = small_font.render(time_text_display, True, config_utils.BLACK)
        time_rect = time_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        screen.blit(time_text, time_rect)
        
        pygame.display.flip()
        clock.tick(FPS) 

# ----------------- 종료 -----------------
close_client_socket()
pygame.quit()
sys.exit()