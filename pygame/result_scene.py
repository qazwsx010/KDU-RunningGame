import pygame
import sys
# config_utils에서 랭킹 함수 및 상수 임포트
from config_utils import load_high_scores, save_high_scores, clear_high_scores 

# ----------------- 결과 화면 씬 클래스 -----------------

class ResultScene:
    def __init__(self, screen_size, time_record, is_win):
        self.time = round(time_record, 2)
        self.is_win = is_win
        self.is_running = True
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen_size

        self.high_scores = load_high_scores()
        self.rank, self.is_ranked = self._check_rank_and_update(save_if_ranked=True)
        
        # 폰트 로딩 (안전하게)
        try:
            self.font_big = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 80)
            self.font_medium = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 45)
            self.font_small = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 30)
        except Exception:
            self.font_big = pygame.font.Font(None, 80)
            self.font_medium = pygame.font.Font(None, 45)
            self.font_small = pygame.font.Font(None, 30)

    def _check_rank_and_update(self, save_if_ranked=True):
        """현재 기록을 검사하고, Top 3에 들면 파일을 업데이트합니다."""
        
        all_scores = [s for s in self.high_scores if s < 99999.0]
        
        if self.time < 99999.0:
            all_scores.append(self.time)
            
        all_scores.sort()
        
        # 현재 기록의 순위 계산
        rank = len([s for s in all_scores if s < self.time]) + 1
        
        is_ranked = rank <= 3
        
        if save_if_ranked and self.is_win and is_ranked:
            new_scores = self.high_scores + [self.time]
            # config_utils의 save_high_scores 사용
            save_high_scores(new_scores)
            self.high_scores = load_high_scores()
            
        return rank, is_ranked

    def process_input(self, events):
        """입력 이벤트를 처리합니다. (재시작, 종료, 랭킹 초기화)"""
        keys_held = pygame.key.get_pressed()
        
        # 1. 랭킹 초기화 (L-SHIFT + ENTER)
        if keys_held[pygame.K_LSHIFT] and keys_held[pygame.K_RETURN]:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    pass
            
            # config_utils의 clear_high_scores 사용
            clear_high_scores()
            self.high_scores = load_high_scores() 
            self.rank, self.is_ranked = self._check_rank_and_update(save_if_ranked=False)
        
        # 2. 개별 키 입력 처리 (ESC, ENTER)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not keys_held[pygame.K_LSHIFT]: 
                        self.is_running = False # False가 되면 main_game에서 reset_game()을 호출함
                elif event.key == pygame.K_ESCAPE:
                    # 💥 pygame.quit() 대신, main_game의 메인 루프를 탈출하도록 신호를 보냅니다.
                    #    가장 간단한 방법은 pygame에 QUIT 이벤트를 직접 보내는 것입니다.
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            
    def render(self, screen):
        """화면을 렌더링합니다."""
        screen.fill((20, 20, 50))
        center_x = self.SCREEN_WIDTH // 2
        
        # 1. 승패 텍스트
        title_text = "승리!" if self.is_win else "패배..."
        title_color = (0, 255, 0) if self.is_win else (255, 0, 0)
        title_surface = self.font_big.render(title_text, True, title_color)
        screen.blit(title_surface, title_surface.get_rect(center=(center_x, 100)))

        # 2. 시간 표시
        time_display = f"{self.time}초" if self.time < 99999.0 else "기록 없음"
        time_text = f"기록: {time_display}"
        time_surface = self.font_medium.render(time_text, True, (255, 255, 255))
        screen.blit(time_surface, time_surface.get_rect(center=(center_x, 200)))
        
        # 3. 랭킹 여부 표시
        if self.is_ranked and self.is_win:
            rank_text = f"★ {self.rank}위 달성! TOP 3 진입! ★"
            color = (255, 215, 0)
        else:
            rank_text = f"순위: {self.rank}위"
            color = (200, 200, 200)
            
        rank_surface = self.font_medium.render(rank_text, True, color)
        screen.blit(rank_surface, rank_surface.get_rect(center=(center_x, 280)))
        
        # 4. 최고 기록 목록
        score_y_start = 380
        title_surface = self.font_medium.render("TOP 3 BEST TIMES", True, (150, 150, 255))
        screen.blit(title_surface, title_surface.get_rect(center=(center_x, score_y_start)))

        for i, score in enumerate(self.high_scores):
            score_display = f"#{i+1}: {score:.2f} seconds" if score < 99999.0 else f"#{i+1}: ---"
            score_text = self.font_medium.render(score_display, True, (255, 255, 255))
            text_rect = score_text.get_rect(center=(center_x, score_y_start + 60 + i * 50))
            screen.blit(score_text, text_rect)
            
        # 5. 재시작/초기화 힌트
        hint_text = "ENTER: 재시작 | ESC: 종료 | L-SHIFT + ENTER: 랭킹 초기화"
        hint_surface = self.font_small.render(hint_text, True, (100, 100, 100))
        screen.blit(hint_surface, hint_surface.get_rect(center=(center_x, self.SCREEN_HEIGHT - 30)))
        
        pygame.display.flip()