import pygame
import sys
import time
import os

# ----------------- 전역 변수 설정 -----------------

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
COUNTDOWN_SIZE = 300

# ----------------- 로딩 헬퍼 함수 -----------------

def load_and_scale_image(path, size, fallback_color):
    """
    이미지를 로드하거나 실패 시 대체 텍스트/서피스를 만듭니다.
    (이 함수는 pygame.init() 이후에 호출되어야 합니다.)
    """
    try:
        img = pygame.image.load(path) 
        img = pygame.transform.scale(img, (size, size))
        return img
    except (pygame.error, FileNotFoundError) as e:
        # 이미지 로드 실패 시, 대체 텍스트(숫자)로 대체
        font_large = pygame.font.Font(None, COUNTDOWN_SIZE)
        
        # 파일명에 따라 대체 텍스트를 결정합니다. (3 -> 2 -> 1 순서)
        if '1.png' in path:
            return font_large.render("3", True, RED)
        elif '22222.png' in path:
            return font_large.render("2", True, RED)
        elif '11111.png' in path:
            return font_large.render("1", True, RED)
        
        temp_surface = pygame.Surface((size, size))
        temp_surface.fill(fallback_color)
        return temp_surface


def run_countdown_scene(screen, draw_track_func):
    """
    3-2-1 카운트다운 씬을 실행하고 게임 시작 시간을 반환합니다.
    (RunningGame.py에서 pygame.init()을 호출한 후 이 함수를 호출해야 합니다.)
    """
    
    # 💡 [수정] 폰트 및 이미지 로딩을 함수 호출 시점으로 이동하여 안전성 확보
    
    GO_FONT = pygame.font.Font(None, 200) 
    
    try:
        COUNTDOWN_IMAGES = [
            load_and_scale_image("countdown1.png", COUNTDOWN_SIZE, RED),      # 3 
            load_and_scale_image("countdown22222.png", COUNTDOWN_SIZE, RED),  # 2 
            load_and_scale_image("countdown11111.png", COUNTDOWN_SIZE, RED)   # 1 
        ]
    except:
        font_large = pygame.font.Font(None, COUNTDOWN_SIZE)
        COUNTDOWN_IMAGES = [
            font_large.render("3", True, RED),
            font_large.render("2", True, RED),
            font_large.render("1", True, RED)
        ]
        
    screen_width, screen_height = screen.get_size()
    go_text = GO_FONT.render("GO!", True, BLACK)
    go_rect = go_text.get_rect(center=(screen_width // 2, screen_height // 2))

    # 1. 3-2-1 카운트다운
    for i, img in enumerate(COUNTDOWN_IMAGES):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                # 💥 pygame.quit() 대신 None을 반환해서 종료 신호를 보냅니다.
                return None

        draw_track_func() 

        img_rect = img.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(img, img_rect)
        
        pygame.display.flip()
        
        time.sleep(1.0) 
        
    # 2. 'GO!' 표시
    draw_track_func()
    screen.blit(go_text, go_rect)
    pygame.display.flip()
    time.sleep(0.5) 

    print("--- GO! 게임 시작! ---")
    
    return time.time()