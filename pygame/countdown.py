import pygame
import sys
import time
# import os # os 모듈은 더 이상 필요하지 않아 제거하거나 주석 처리합니다.

# ----------------- 전역 변수 설정 -----------------

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
COUNTDOWN_SIZE = 400 # ⭐️ 크기를 400으로 키움 (기존 300)
GO_SIZE = 300          # ⭐️ GO! 텍스트 크기 추가
OUTLINE_OFFSET = 5     # ⭐️ 테두리 효과를 위한 픽셀 오프셋

# ----------------- 로딩 헬퍼 함수 (제거 또는 주석 처리) -----------------
# def load_and_scale_image(path, size, fallback_color):
#     """
#     이미지 로드 로직은 제거하고 폰트 대체 로직만 사용합니다.
#     """
#     # ... 기존 이미지 로딩 및 대체 로직 제거 ...
#     pass


def run_countdown_scene(screen, draw_track_func):
    """
    3-2-1 카운트다운 씬을 실행하고 게임 시작 시간을 반환합니다.
    """
    
    # 💡 폰트 설정 (기존 None 폰트 사용)
    FONT_LARGE = pygame.font.Font(None, COUNTDOWN_SIZE) # 3, 2, 1 폰트
    GO_FONT = pygame.font.Font(None, GO_SIZE)             # ⭐️ GO! 폰트 크기 변경
    
    # 3, 2, 1 카운트다운 텍스트 Surface 생성
    # Note: 테두리 구현을 위해 '본문'과 '외곽선용' 텍스트를 모두 만듭니다.
    COUNTDOWN_SURFACES_BODY = [
        FONT_LARGE.render("3", True, RED),
        FONT_LARGE.render("2", True, RED),
        FONT_LARGE.render("1", True, RED)
    ]
    # 외곽선용 (검은색) 텍스트 생성
    COUNTDOWN_SURFACES_OUTLINE = [
        FONT_LARGE.render("3", True, BLACK),
        FONT_LARGE.render("2", True, BLACK),
        FONT_LARGE.render("1", True, BLACK)
    ]
        
    screen_width, screen_height = screen.get_size()
    # ⭐️ GO! 텍스트를 빨간색(RED)으로 변경 ⭐️
    go_text = GO_FONT.render("GO!", True, RED) 
    go_rect = go_text.get_rect(center=(screen_width // 2, screen_height // 2))

    # 1. 3-2-1 카운트다운
    for i, body_surface in enumerate(COUNTDOWN_SURFACES_BODY): 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return None

        draw_track_func() 
        
        outline_surface = COUNTDOWN_SURFACES_OUTLINE[i]
        
        # ⭐️ 테두리 구현 로직 ⭐️
        
        # 1. 외곽선(검은색)을 먼저 그립니다.
        # 중심을 기준으로 상하좌우로 OUTLINE_OFFSET 만큼 이동하여 4개의 외곽선 서피스를 그립니다.
        center_x, center_y = screen_width // 2, screen_height // 2
        
        for dx in [-OUTLINE_OFFSET, OUTLINE_OFFSET]:
            for dy in [-OUTLINE_OFFSET, OUTLINE_OFFSET]:
                outline_rect = outline_surface.get_rect(center=(center_x + dx, center_y + dy))
                screen.blit(outline_surface, outline_rect)

        # 2. 본문(빨간색)을 중앙에 덮어씁니다.
        body_rect = body_surface.get_rect(center=(center_x, center_y))
        screen.blit(body_surface, body_rect)
        
        pygame.display.flip()
        
        time.sleep(1.0) 
        
    # 2. 'GO!' 표시
    draw_track_func()
    screen.blit(go_text, go_rect)
    pygame.display.flip()
    time.sleep(0.5) 

    print("--- GO! 게임 시작! ---")
    
    return time.time()

# ----------------- 로딩 헬퍼 함수 호출은 이제 필요 없습니다. -----------------

# (참고: 기존에 있던 load_and_scale_image 함수는 이 수정 방안에서는 제거하거나 주석 처리해야 합니다.)