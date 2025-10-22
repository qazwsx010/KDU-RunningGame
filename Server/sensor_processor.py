# sensor_processor.py

import math
from collections import deque
import config # ⭐ config 파일 import

# --- MPU6050 및 RMS 상수 (config에서 가져옴) ---
ACCEL_SCALE_FACTOR = config.ACCEL_SCALE_FACTOR
G_CONSTANT = config.G_CONSTANT
RMS_N_SAMPLES = config.RMS_N_SAMPLES

# --- 전역 상태 변수 ---
# 💡 RMS 계산을 위한 Movement_A 버퍼
RMS_BUFFER = deque(maxlen=RMS_N_SAMPLES) 
latest_rms_score = 0.0 # RMS 필터링 후의 최종 Score (main_server에서 접근)


def calculate_movement_a(raw_data):
    """
    MPU6050 Raw 데이터로부터 순수한 운동 가속도 (Movement_A)를 계산합니다.
    Movement_A = |가속도 벡터 크기 - 1.0g|
    """
    
    # 1. 가속도 성분 계산 (g 단위)
    ax = raw_data.get('ax', 0)
    ay = raw_data.get('ay', 0)
    az = raw_data.get('az', 0)

    ax_g = ax / ACCEL_SCALE_FACTOR
    ay_g = ay / ACCEL_SCALE_FACTOR
    az_g = az / ACCEL_SCALE_FACTOR

    # 2. 가속도 벡터 크기 계산 (magnitude_g)
    sum_of_squares = ax_g**2 + ay_g**2 + az_g**2
    magnitude_g = math.sqrt(sum_of_squares)
    
    # 3. 순수한 운동 가속도 (Movement_A) 계산
    movement_a = abs(magnitude_g - G_CONSTANT)
    
    return {'magnitude': magnitude_g, 'movement_a': movement_a}


def calculate_rms_score(movement_a):
    """
    RMS_BUFFER의 데이터와 새로운 movement_a를 사용하여 RMS Score를 계산합니다.
    """
    global RMS_BUFFER, latest_rms_score
    
    # 1. 버퍼 업데이트
    RMS_BUFFER.append(movement_a)
    
    # 2. 현재 유효 데이터 개수 (M) 확인
    current_M = len(RMS_BUFFER)
    
    if current_M == 0:
        latest_rms_score = 0.0
        return 0.0
    
    # 3. RMS 계산
    try:
        sum_of_squares = sum(x**2 for x in RMS_BUFFER)
        current_rms = math.sqrt(sum_of_squares / current_M)
        
        latest_rms_score = current_rms
        return current_rms
        
    except Exception as e:
        print(f"RMS Calculation Error: {e}")
        latest_rms_score = 0.0
        return 0.0