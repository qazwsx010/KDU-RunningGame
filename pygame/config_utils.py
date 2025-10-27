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
# 💡 캐릭터 크기를 50 * 4 (200px)에서 50 * 6 (300px)로 키웠습니다.
BOX_SIZE = 50 * 9 
box_center_offset = (BOX_SIZE / 2)
AI_SPEED = 0.5 * 3
PLAYER_SPEED_CORRECTION = 0.22

# ----------------- 💡 에셋 전역 변수 -----------------
ai_image = None
player_image = None
ai_frames = []
player_frames = [] 
AI_FRAME_DURATION_MS = 0

# ----------------- ⭐️ 로컬 파일 로딩 설정 (단일 이미지 사용) -----------------
# 💡 배경 이미지 경로 resource/background.png 가정
BACKGROUND_RESOURCE_FOLDER = os.path.join("resource")
BACKGROUND_IMAGE_FILE = "background.png"
BACKGROUND_IMAGE = None # 이미지가 로드될 변수

# 💡 AI 이미지 경로: resource/Gyeongdong.png 가정
RESOURCE_FOLDER = os.path.join("resource") 
AI_IMAGE_FILE = "Gyeongdong.png" # AI 캐릭터의 단일 이미지 파일명
FRAME_COUNT_REPLICATE = 67 # main_game.py의 인덱스 접근 오류 방지를 위해 복제할 프레임 수 (AI_FRAME_END_INDEX + 1)

# 💡 플레이어 이미지 경로: resource/Ghost.png 가정
PLAYER_RESOURCE_FOLDER = os.path.join("resource")
PLAYER_IMAGE_FILE = "Ghost.png" # 플레이어 캐릭터의 단일 이미지 파일명

# ----------------- ⭐️ Base64 폴백 이미지 (단일 이미지) -----------------
# 🚨 이 Base64는 여전히 더미 이미지이므로, 실제 유령/사자 캐릭터의 Base64 데이터로 교체해야 합니다.
AI_BASE64_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAADElEQVR42mP4z8BQMAH+gYDFGBkAAIkBAj8Vd+sAAAAASUVORK5CYII="
PLAYER_BASE64_IMAGE = "iVBORw0KGgoAAAANFAAAAACklEQVR42mP4/5+BQQAEEQoCAZ5QxQAAAABJRU5ErkJggg=="


# ----------------- ⭐️ 단일 이미지 로딩 함수 -----------------
def load_local_single_image(folder_path, file_name, size):
    """지정된 로컬 폴더에서 단일 이미지 파일을 로드합니다."""
    
    # config_utils.py가 있는 절대 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 🚨 경로 계산: 현재 디렉토리에서 한 단계 위 (..)로 올라가서 RESOURCE_FOLDER를 찾습니다.
    # 만약 resource 폴더가 config_utils.py와 같은 폴더에 있다면 "..", 를 제거하세요.
    full_path = os.path.join(current_dir, "..", folder_path, file_name) 
    
    print("-" * 50)
    print(f"1. config_utils.py 위치: {current_dir}")
    normalized_path = os.path.normpath(full_path)
    print(f"2. 계산된 에셋 경로 (정규화): {normalized_path}")
    print("-" * 50)

    if not os.path.exists(normalized_path):
        print(f"[ERROR] 🚫 파일을 찾을 수 없음: {normalized_path}. Base64 폴백 시도.")
        return None
    
    try:
        surf = pygame.image.load(normalized_path).convert_alpha()
        # 로드된 이미지를 지정된 크기(size)로 스케일링합니다.
        scaled_surf = pygame.transform.scale(surf, (size, size))
        print(f"[SUCCESS] 로컬 파일 시스템에서 단일 이미지 로드 완료: {file_name}")
        return scaled_surf
    
    except pygame.error as e:
        print(f"[FALLBACK] ❌ 로컬 파일 로드 실패 (Pygame 에러: {e}). Base64 로드 시도.")
        return None
    except Exception as e:
        print(f"[ERROR] ❌ 로컬 파일 로드 중 기타 예외 발생: {e}")
        return None

# ----------------- Base64 단일 이미지 로딩 함수 -----------------
def load_base64_single_image(base64_data, size):
    """Base64 데이터를 로드하여 단일 Pygame Surface를 반환합니다."""
    if not base64_data:
        return None
    
    try:
        image_data = base64.b64decode(base64_data)
        image_file = io.BytesIO(image_data)
        original_surf = pygame.image.load(image_file).convert_alpha() 
        # 로드된 이미지를 지정된 크기(size)로 스케일링합니다.
        scaled_surf = pygame.transform.scale(original_surf, (size, size))
        
        return scaled_surf

    except Exception as e:
        print(f"[ERROR] Base64 이미지 로드 실패: {e}. 컬러 박스로 대체됩니다.")
        return None

# ----------------- 컬러 박스 프레임 생성 함수 (최후의 폴백) -----------------
def create_temp_frames(colors, texts, size, frame_count=FRAME_COUNT_REPLICATE):
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
    
    # 🚨 프레임 수 계산 (FRAME_COUNT_REPLICATE)
    for i in range(frame_count): 
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
    global BACKGROUND_IMAGE
    # 1. AI 단일 이미지 로드 (로컬 파일 > Base64 > 컬러 박스 순)
    
    # 1.1 로컬 파일 로드 시도
    ai_surf = load_local_single_image(RESOURCE_FOLDER, AI_IMAGE_FILE, ai_size)
    
    if ai_surf is None:
        # 1.2 Base64 폴백 시도
        ai_surf = load_base64_single_image(AI_BASE64_IMAGE, ai_size)
        
        if ai_surf is None:
            # 1.3 최후의 폴백: 컬러 박스 생성
            print("[CRITICAL FALLBACK] AI 프레임: 컬러 박스 사용")
            ai_frames = create_temp_frames([(255, 0, 0), (200, 50, 0)], ["AI", "GO"], ai_size, FRAME_COUNT_REPLICATE)
        else:
            print("[FALLBACK] AI 프레임: Base64 이미지 사용")
            # 단일 이미지를 필요한 프레임 수만큼 복제하여 리스트에 채웁니다.
            ai_frames = [ai_surf.copy() for _ in range(FRAME_COUNT_REPLICATE)]
    else:
        print("[SUCCESS] AI 프레임: 로컬 단일 이미지 로드 성공.")
        # 단일 이미지를 필요한 프레임 수만큼 복제하여 리스트에 채웁니다.
        ai_frames = [ai_surf.copy() for _ in range(FRAME_COUNT_REPLICATE)]
    
    
    # 2. 플레이어 단일 이미지 로드 (로컬 파일 > Base64 > 컬러 박스 순)
    
    # 2.1 로컬 파일 로드 시도
    player_surf = load_local_single_image(PLAYER_RESOURCE_FOLDER, PLAYER_IMAGE_FILE, ai_size)
    
    if player_surf is None:
        # 2.2 Base64 폴백 시도
        player_surf = load_base64_single_image(PLAYER_BASE64_IMAGE, ai_size)
        
        if player_surf is None:
            # 2.3 최후의 폴백: 컬러 박스 생성
            print("[CRITICAL FALLBACK] 플레이어 프레임: 컬러 박스 사용")
            player_frames = create_temp_frames([(0, 0, 255), (0, 100, 255)], ["YOU", "RUN"], ai_size, FRAME_COUNT_REPLICATE)
        else:
            print("[FALLBACK] 플레이어 프레임: Base64 이미지 사용")
            # 단일 이미지를 필요한 프레임 수만큼 복제하여 리스트에 채웁니다.
            player_frames = [player_surf.copy() for _ in range(FRAME_COUNT_REPLICATE)]
    else:
        print("[SUCCESS] 플레이어 프레임: 로컬 단일 이미지 로드 성공.")
        # 단일 이미지를 필요한 프레임 수만큼 복제하여 리스트에 채웁니다.
        player_frames = [player_surf.copy() for _ in range(FRAME_COUNT_REPLICATE)]
    
    # 3. 각 프레임당 지속 시간 계산 (총 0.3초)
    total_frames = len(ai_frames)
    if total_frames > 0:
        AI_FRAME_DURATION_MS = (300 / total_frames) 
    else:
        AI_FRAME_DURATION_MS = 1000 
        
    # 4. 단일 이미지 변수 설정 (복제된 프레임의 첫 번째 요소 사용)
    ai_image = ai_frames[0] if ai_frames else pygame.Surface((ai_size, ai_size))
    player_image = player_frames[0] if player_frames else pygame.Surface((ai_size, ai_size))

    # ----------------- 5. ⭐️ 배경 이미지 로드 로직 추가 ⭐️ -----------------
    print("--- 5. 배경 이미지 로드 시도 ---")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 🚨 AI/플레이어 이미지 로드 로직과 동일하게 상위 폴더 ("..")를 참조합니다.
    # 즉, config_utils.py가 있는 폴더의 상위 폴더에서 resource를 찾습니다.
    full_path = os.path.join(
        current_dir, 
        "..", # <- 이 부분이 핵심! (config_utils가 하위 폴더에 있을 경우)
        BACKGROUND_RESOURCE_FOLDER, 
        BACKGROUND_IMAGE_FILE
    ) 
    normalized_path = os.path.normpath(full_path)
    
    print(f"DEBUG: 배경 이미지 예상 경로: {normalized_path}")
    
    if os.path.exists(normalized_path):
        try:
            # 배경 이미지는 크기 조정 없이 원본을 로드하고 투명도 처리가 불필요하여 .convert() 사용
            BACKGROUND_IMAGE = pygame.image.load(normalized_path).convert()
            print(f"[SUCCESS] 배경 이미지 로컬 로드 완료: {normalized_path}")
        except pygame.error as e:
            print(f"[ERROR] ❌ 배경 이미지 로드 실패 (Pygame 에러: {e}). 배경 없음.")
            BACKGROUND_IMAGE = None
    else:
        # 🚨 폴백: 만약 resource 폴더가 config_utils.py와 같은 폴더에 있다면 (상위 폴더 참조 불필요)
        full_path_no_up = os.path.join(current_dir, BACKGROUND_RESOURCE_FOLDER, BACKGROUND_IMAGE_FILE)
        normalized_path_no_up = os.path.normpath(full_path_no_up)
        
        if os.path.exists(normalized_path_no_up):
             try:
                BACKGROUND_IMAGE = pygame.image.load(normalized_path_no_up).convert()
                print(f"[SUCCESS] 배경 이미지 로컬 로드 완료 (폴백 경로).")
             except pygame.error as e:
                print(f"[ERROR] ❌ 배경 이미지 로드 실패 (Pygame 에러: {e}). 배경 없음.")
                BACKGROUND_IMAGE = None
        else:
            print(f"[ERROR] 🚫 배경 이미지 파일을 찾을 수 없음: {normalized_path} 또는 {normalized_path_no_up}. 배경 없음.")
            BACKGROUND_IMAGE = None
    # -----------------------------------------------------------------


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
