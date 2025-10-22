import pygame
import os
import sys
import io 
import base64 

# ----------------- 랭킹 파일 설정 -----------------
HIGH_SCORE_FILE = "high_scores.txt"
INITIAL_HIGH_SCORES = [99999.0, 99999.0, 99999.0] 

# ----------------- 색상 및 상수 설정 -----------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0) 

# 캐릭터 및 속도 설정 (main_game에서 사용)
BOX_SIZE = 50 * 4 
box_center_offset = (BOX_SIZE / 2)
AI_SPEED = 0.5 * 3
PLAYER_SPEED_CORRECTION = 0.22

# ----------------- 💡 에셋 전역 변수 -----------------
ai_image = None
player_image = None
ai_frames = []
player_frames = [] 
AI_FRAME_DURATION_MS = 0

# ----------------- ⭐️ 로컬 파일 로딩 설정 (VS Code 환경용) -----------------
# 💡 AI 프레임 경로: RunningGame/파이게임 -> ../리소스/AI_Runner
RESOURCE_FOLDER = os.path.join("resource", "AICharacter") 
AI_FRAME_BASE_NAME = "frame_" 
AI_FRAME_START_INDEX = 0
AI_FRAME_END_INDEX = 66 

# 💡 플레이어 프레임 경로 정의 (AI와 동일한 '리소스' 폴더 내의 'Player_Runner' 가정)
PLAYER_RESOURCE_FOLDER = os.path.join("resource", "PlayerCharacter")
PLAYER_FRAME_BASE_NAME = "frame_" 
PLAYER_FRAME_START_INDEX = 0
PLAYER_FRAME_END_INDEX = 34 
# ----------------- ⭐️ Base64 폴백 이미지 (로컬 로드 실패 시 사용) -----------------
AI_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAADElEQVR42mP4z8BQMAH+gYDFGBkAAIkBAj8Vd+sAAAAASUVORK5CYII="
PLAYER_BASE64_IMAGE = "iVBORw0KGgoAAAANFAAAAACklEQVR42mP4/5+BQQAEEQoCAZ5QxQAAAABJRU5ErkJggg=="


# ----------------- ⭐️ 로컬 파일 로딩 함수 (VS Code 환경용) -----------------
def load_local_frames(folder_path, base_name, start_idx, end_idx, size):
    """지정된 로컬 폴더에서 이미지 파일을 순차적으로 로드합니다."""
    frames = []
    
    # 🚨 파일 이름에 5자리 0 채우기(zero-padding)를 적용하는 헬퍼 함수
    def get_padded_filename(index):
        # 예: index=0 -> "frame_00000.png"
        return f"{base_name}{index:05d}.png"
    
    # config_utils.py가 있는 절대 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 🚨 경로 계산: 현재 디렉토리에서 한 단계 위 (..)로 올라가서 RESOURCE_FOLDER를 찾습니다.
    full_folder_path = os.path.join(current_dir, "..", folder_path) 
    
    print("-" * 50)
    print(f"1. config_utils.py 위치: {current_dir}")
    # 💡 경로 문제 해결을 위해 os.path.normpath를 사용하여 경로를 정리합니다.
    normalized_path = os.path.normpath(full_folder_path)
    print(f"2. 계산된 에셋 폴더 경로 (정규화): {normalized_path}")
    print("-" * 50)

    if not os.path.isdir(normalized_path):
        print(f"[ERROR] 🚫 폴더를 찾을 수 없음: {normalized_path}. Base64 폴백 사용.")
        return []
    
    try:
        # 첫 번째 파일만 테스트 로드 (00000으로 시작)
        test_filename = get_padded_filename(start_idx) 
        test_path = os.path.join(normalized_path, test_filename)
        
        if not os.path.exists(test_path):
            print(f"[ERROR] 🚫 첫 번째 파일({test_filename}) 찾을 수 없음: {test_path}")
            return []
            
        print(f"[INFO] ✅ 첫 번째 파일 로드 테스트 성공: {test_path}")

        # 전체 파일 로드 시작 (0부터 66까지)
        for i in range(start_idx, end_idx + 1):
            filename = get_padded_filename(i) 
            path = os.path.join(normalized_path, filename)
            
            if not os.path.exists(path):
                print(f"[WARNING] 파일 없음: {path}. 로딩 중단.")
                return [] 
                
            surf = pygame.image.load(path).convert_alpha()
            scaled_surf = pygame.transform.scale(surf, (size, size))
            frames.append(scaled_surf)
        
        print(f"[SUCCESS] 로컬 파일 시스템에서 {len(frames)}개의 프레임 로드 완료.")
        return frames
    
    except pygame.error as e:
        print(f"[FALLBACK] ❌ 로컬 파일 로드 실패 (Pygame 에러: {e}). Base64 로드 시도.")
        return []
    except Exception as e:
        print(f"[ERROR] ❌ 로컬 파일 로드 중 기타 예외 발생: {e}")
        return []

# ----------------- Base64 프레임 생성 함수 (폴백) -----------------
def load_base64_frames(base64_data, frame_count, size, is_player=False):
    """Base64 데이터를 로드하여 여러 프레임으로 복제 (애니메이션 시뮬레이션용)"""
    if not base64_data:
        return []
    
    try:
        image_data = base64.b64decode(base64_data)
        image_file = io.BytesIO(image_data)
        # Pygame 로드 시도 (여기서 libpng 오류가 나는 경우, Base64 이미지 자체의 문제일 수 있습니다.)
        original_surf = pygame.image.load(image_file).convert_alpha() 
        scaled_surf = pygame.transform.scale(original_surf, (size, size))
        
        frames = []
        for i in range(frame_count):
            frame = scaled_surf.copy()
            frames.append(frame)
        
        return frames

    except Exception as e:
        # Base64 이미지 로드 오류 발생 시
        print(f"[ERROR] Base64 이미지 로드 실패: {e}. 컬러 박스로 대체됩니다.")
        return []

# ----------------- 컬러 박스 프레임 생성 함수 (최후의 폴백) -----------------
def create_temp_frames(colors, texts, size, frame_count=AI_FRAME_END_INDEX):
    """애니메이션 시각화를 위해 색상과 텍스트가 변하는 Pygame Surface 프레임을 생성합니다 (최후의 폴백)."""
    frames = []
    size_tuple = (size, size)
    font = pygame.font.Font(None, int(size * 0.4)) 
    
    # AI용 텍스트
    ai_temp_colors = [(255, 0, 0), (200, 50, 0)]
    ai_temp_texts = ["AI", "GO"]
    
    # 플레이어용 텍스트
    player_temp_colors = [(0, 0, 255), (0, 100, 255)]
    player_temp_texts = ["YOU", "RUN"]

    if texts[0] == "YOU": # 플레이어 프레임 생성 시
        temp_colors = player_temp_colors
        temp_texts = player_temp_texts
    else: # AI 프레임 생성 시
        temp_colors = ai_temp_colors
        temp_texts = ai_temp_texts
    
    # 🚨 프레임 수 계산 시 +1을 해서 총 67프레임이 되도록 함
    for i in range(frame_count + 1): 
        surf = pygame.Surface(size_tuple, pygame.SRCALPHA)
        surf.fill(temp_colors[i % len(temp_colors)])
        text_surface = font.render(temp_texts[i % len(temp_colors)], True, WHITE)
        text_rect = text_surface.get_rect(center=(size // 2, size // 2))
        surf.blit(text_surface, text_rect)
        frames.append(surf)
    return frames
    
# ----------------- 💡 핵심 에셋 초기화 함수 -----------------

def init_assets(ai_size):
    """모든 에셋을 로드하고 config_utils 모듈의 전역 변수에 할당합니다."""
    global ai_image, player_image, ai_frames, player_frames, AI_FRAME_DURATION_MS
    
    # 1. AI 애니메이션 프레임 로드 시도 (로컬 파일 > Base64 > 컬러 박스 순)
    ai_frames = load_local_frames(RESOURCE_FOLDER, AI_FRAME_BASE_NAME, AI_FRAME_START_INDEX, AI_FRAME_END_INDEX, ai_size)
    
    if not ai_frames:
        # 로컬 파일 로드 실패 시 Base64 재시도 (이미지가 손상된 경우도 고려)
        ai_frames = load_base64_frames(AI_BASE64_IMAGE, AI_FRAME_END_INDEX + 1, ai_size, is_player=False)
        
        if not ai_frames:
            print("[CRITICAL FALLBACK] AI 프레임: 컬러 박스 사용")
            # 컬러 박스에 "AI" 텍스트를 넣기 위해 텍스트 인수로 구분
            ai_frames = create_temp_frames([(255, 0, 0), (200, 50, 0)], ["AI", "GO"], ai_size, AI_FRAME_END_INDEX)
        else:
            print("[FALLBACK] AI 프레임: Base64 이미지 사용 (단일 이미지 복제)")
    else:
        print("[SUCCESS] AI 프레임: 로컬 67개 파일 로드 성공.")
    
    # 2. 플레이어 애니메이션 프레임 로드 시도 (로컬 파일 > Base64 > 컬러 박스 순)
    # 💡 AI와 동일한 로드 함수(load_local_frames)를 사용하되, 플레이어 전용 경로/이름/인덱스 상수를 사용
    player_frames = load_local_frames(PLAYER_RESOURCE_FOLDER, PLAYER_FRAME_BASE_NAME, PLAYER_FRAME_START_INDEX, PLAYER_FRAME_END_INDEX, ai_size)
    
    if not player_frames:
        # 로컬 로드 실패 시 Base64 폴백 시도
        player_frames = load_base64_frames(PLAYER_BASE64_IMAGE, AI_FRAME_END_INDEX + 1, ai_size, is_player=True) # 67개 프레임
        
        if not player_frames:
            print("[CRITICAL FALLBACK] 플레이어 프레임: 컬러 박스 사용")
            # 컬러 박스에 "YOU" 텍스트를 넣기 위해 텍스트 인수로 구분
            player_frames = create_temp_frames([(0, 0, 255), (0, 100, 255)], ["YOU", "RUN"], ai_size, AI_FRAME_END_INDEX)
        else:
            print("[FALLBACK] 플레이어 프레임: Base64 이미지 사용 (단일 이미지 복제)")
    else:
        print("[SUCCESS] 플레이어 프레임: 로컬 67개 파일 로드 성공.")

    
    # 3. 각 프레임당 지속 시간 계산 (총 0.3초)
    total_frames = len(ai_frames)
    if total_frames > 0:
        AI_FRAME_DURATION_MS = (300 / total_frames) 
    else:
        AI_FRAME_DURATION_MS = 1000 
        
    # 4. 단일 이미지 변수 설정 (애니메이션 프레임의 첫 번째 요소 사용)
    ai_image = ai_frames[0] if ai_frames else pygame.Surface((ai_size, ai_size))
    player_image = player_frames[0] if player_frames else pygame.Surface((ai_size, ai_size))


# ----------------- 랭킹 파일 처리 함수 -----------------
def load_high_scores():
    if not os.path.exists(HIGH_SCORE_FILE):
        return INITIAL_HIGH_SCORES[:]
    scores = []
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            for line in f:
                scores.append(float(line.strip()))
        scores = sorted([s for s in scores if s < 99999.0])[:3]
        while len(scores) < 3: scores.append(99999.0)
    except Exception:
        return INITIAL_HIGH_SCORES[:]
    return scores

def save_high_scores(scores):
    try:
        valid_scores = sorted([s for s in scores if s < 99999.0])[:3]
        with open(HIGH_SCORE_FILE, 'w') as f:
            for score in valid_scores:
                f.write(f"{score:.2f}\n") 
    except Exception as e:
        print(f"[기록 오류] 파일 저장 중 예외 발생: {e}")

def clear_high_scores():
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            pass
        print("--- 🗑️ 최고 기록이 초기화되었습니다. ---")
    except Exception as e:
        print(f"[기록 오류] 초기화 중 예외 발생: {e}")