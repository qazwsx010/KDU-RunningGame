# config.py

# --- BLE UUID 설정 ---
BLE_SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"
BLE_CHARACTERISTIC_UUID = "abcd1234-5678-90ab-cdef-1234567890ab"
BLE_TARGET_NAME = "RUNNIG_BOARD_1" # <------------- 변경필요

# --- TCP/IP 설정 ---
TCP_HOST = '127.0.0.1'  
TCP_PORT = 65432
MAX_TCP_CONNECTIONS = 1
TCP_SEND_INTERVAL_MS = 30 # 전송 주기 (ms)

# --- 센서 계산 상수 (sensor_processor.py에서 사용) ---
ACCEL_SCALE_FACTOR = 4096.0
G_CONSTANT = 1.0 
RMS_N_SAMPLES = 8 # RMS 계산에 사용할 샘플 개수 (N)

# --- 속도 제어 상수 (main_server.py에서 사용) ---
TARGET_MAX_SPEED = 7.04 

# ⭐️ Dead Zone: 정지 시 노이즈 RMS 값을 실험적으로 구한 값
RMS_DEAD_ZONE = 0.05
# ⭐️ MAX Score: 사용자가 최대로 흔들 때의 RMS 값 (실험을 통해 조정 필요)
RMS_MAX_SCORE = 0.8
# ⭐️ 활성 범위
RMS_ACTIVE_RANGE = RMS_MAX_SCORE - RMS_DEAD_ZONE 

# ⭐️ 모멘텀 및 가속 설정
ACCELERATION_RATE = 1.5 

# 💡 센서 오버플로우/비정상 값 처리 임계값 추가
ERROR_SCORE_THRESHOLD = 50.0