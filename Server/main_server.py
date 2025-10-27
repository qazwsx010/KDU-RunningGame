# main_server.py (메인 서버 파일)

import asyncio
from bleak import BleakClient, BleakScanner
import json
import socket
import threading
import time

# ⭐⭐ 분리된 모듈 import ⭐⭐
import config 
import sensor_processor as sp 


# --- 전역 상태 변수 (통신 및 제어 관련만 유지) ---
tcp_clients = [] 
PREVIOUS_APPLIED_SPEED = 0.0 

# --- 2. BLE 콜백 함수 --- (계산 함수만 변경)
def ble_data_callback(sender, data):
    """BLE로부터 데이터를 수신하여 Movement_A를 계산하고 RMS 버퍼에 추가합니다."""
    try:
        text = data.decode("utf-8")
        raw_data = json.loads(text)
        
        # 1. Movement_A 계산 (sp 모듈 함수 사용)
        processed_data = sp.calculate_movement_a(raw_data)
        
        # 2. RMS Score 계산 및 버퍼 업데이트 (sp 모듈 함수 사용)
        rms_score = sp.calculate_rms_score(processed_data['movement_a'])

        # ⭐️ 실시간 출력 (Raw Data와 필터링 결과 모두 표시)
        """print(f"BLE <- Raw A({raw_data['ax']}, {raw_data['ay']}, {raw_data['az']}) | "
              f"Mov_A: {processed_data['movement_a']:.4f} | "
              f"RMS Score: {rms_score:.4f} ({len(sp.RMS_BUFFER)}/{config.RMS_N_SAMPLES})")"""

    except json.JSONDecodeError:
        print("BLE Error: Received malformed JSON.")
    except Exception as e:
        print(f"BLE Error in callback: {e}")

# --- 3. TCP 서버 스레드 (RMS 기반 속도, Dead Zone, 모멘텀 로직) ---
def tcp_server_thread():
    """TCP 서버를 실행하고 RMS Score를 최종 속도로 변환하여 전송합니다."""
    global tcp_clients, PREVIOUS_APPLIED_SPEED
    
    # config에서 설정값 로드
    TCP_HOST = config.TCP_HOST
    TCP_PORT = config.TCP_PORT
    MAX_TCP_CONNECTIONS = config.MAX_TCP_CONNECTIONS
    
    TARGET_MAX_SPEED = config.TARGET_MAX_SPEED
    RMS_DEAD_ZONE = config.RMS_DEAD_ZONE
    RMS_ACTIVE_RANGE = config.RMS_ACTIVE_RANGE
    ACCELERATION_RATE = config.ACCELERATION_RATE
    ERROR_SCORE_THRESHOLD = config.ERROR_SCORE_THRESHOLD
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((TCP_HOST, TCP_PORT))
        server_socket.listen(MAX_TCP_CONNECTIONS)
        print(f"\nTCP Server listening on {TCP_HOST}:{TCP_PORT}")
    except Exception as e:
        print(f"TCP Error: Failed to start server: {e}")
        return

    def accept_clients():
        while True:
            try:
                server_socket.settimeout(0.5) 
                client_conn, addr = server_socket.accept()
                client_conn.setblocking(True) 
                
                if len(tcp_clients) >= MAX_TCP_CONNECTIONS:
                    client_conn.close()
                    continue
                    
                tcp_clients.append(client_conn)
                print(f"TCP: Client connected from {addr}. Total: {len(tcp_clients)}")
            except socket.timeout:
                continue
            except Exception:
                break 
    
    threading.Thread(target=accept_clients, daemon=True).start()
    
    # 데이터 전송 루프
    while True:
        # 전송 주기를 config 값으로 설정
        time.sleep(config.TCP_SEND_INTERVAL_MS / 1000.0) 
        
        if not tcp_clients:
            continue
            
        # ⭐⭐ 분리된 모듈의 최종 RMS Score 사용 ⭐⭐
        current_rms_score = sp.latest_rms_score 
        current_applied_speed = 0.0 

        # 1. 에러 값 필터링 
        if current_rms_score >= ERROR_SCORE_THRESHOLD:
            target_speed = 0.0
            current_rms_score = 0.0 
            print(f"[SERVER_ERROR] 비정상적인 RMS Score ({current_rms_score:.4f}) 감지. 0.00 처리.")

        # 2. Dead Zone 처리 및 목표 속도 계산 
        elif current_rms_score <= RMS_DEAD_ZONE: 
            target_speed = 0.0 
        else:
            # Dead Zone을 제외한 활성 점수 계산 및 Target Speed로 스케일링
            active_score = current_rms_score - RMS_DEAD_ZONE
            
            clamped_score = min(active_score, RMS_ACTIVE_RANGE)
            
            target_speed = (clamped_score / RMS_ACTIVE_RANGE) * TARGET_MAX_SPEED

        # 3. 모멘텀 (가속 보상) 로직 적용
        speed_difference = target_speed - PREVIOUS_APPLIED_SPEED
        
        if speed_difference > 0:
            current_applied_speed = PREVIOUS_APPLIED_SPEED + (speed_difference * ACCELERATION_RATE)
        else:
            current_applied_speed = PREVIOUS_APPLIED_SPEED + speed_difference 
            
        # 4. 최대 속도 제한 및 음수 방지
        current_applied_speed = max(0.0, min(current_applied_speed, TARGET_MAX_SPEED))
        
        # 5. 다음 루프를 위해 저장
        PREVIOUS_APPLIED_SPEED = current_applied_speed
            
        # 전송 데이터 생성
        data_to_send = {"speed": current_applied_speed}
        message = json.dumps(data_to_send) + '\n' 
        
        # ⭐️ 실시간 출력
        """print(f"TCP -> RMS Score: {current_rms_score:.4f} | Target Speed: {target_speed:.4f} | "
              f"Applied Speed: {current_applied_speed:.4f}")"""
        
        # 6. 클라이언트 전송
        clients_to_remove = []
        for client_conn in tcp_clients:
            try:
                client_conn.sendall(message.encode('utf-8'))
            except Exception:
                clients_to_remove.append(client_conn)
                
        for client_conn in clients_to_remove:
            tcp_clients.remove(client_conn)
            client_conn.close()
            print(f"TCP: Client disconnected. Total: {len(tcp_clients)}")

# --- 4. Main BLE 실행 함수 --- 
async def ble_run():
    # ⭐⭐ 타겟 장치 이름을 목록으로 정의 ⭐⭐
    TARGET_NAMES = ["RUNNIG_BOARD_1", "RUNNIG_BOARD_2"]
    BLE_CHARACTERISTIC_UUID = config.BLE_CHARACTERISTIC_UUID
    
    # TCP 서버 스레드 시작
    tcp_thread = threading.Thread(target=tcp_server_thread, daemon=True)
    tcp_thread.start()
    
    while True:
        print(f"\n블루투스 찾는중 {' or '.join(TARGET_NAMES)}...")
        try:
            devices = await BleakScanner.discover(timeout=5.0)
        except Exception as e:
            print(f"BLE Error: Scanner failed ({e}). Retrying...")
            await asyncio.sleep(5)
            continue
            
        target = None
        # ⭐⭐ 타겟 이름 목록을 순회하며 일치하는 기기를 찾습니다. ⭐⭐
        for d in devices:
            if d.name in TARGET_NAMES:
                target = d
                break

        if target is None:
            print(f"블루투스 검색 실패. 5초후 재시도")
            await asyncio.sleep(5)
            continue

        try:
            # target 변수에 일치하는 기기가 저장되어 있습니다.
            async with BleakClient(target.address) as client:
                print(f"블루투스 연결 성공\n이름 : {target.name}\n주소 : {target.address}\n")
                
                await client.start_notify(BLE_CHARACTERISTIC_UUID, ble_data_callback)
                print(f"블루투스로 데이터 받는중... \nctrl+C로 종료")

                while client.is_connected:
                    await asyncio.sleep(1)
            
            print("BLE: Disconnected. Reconnecting...")
            
        except Exception as e:
            print(f"BLE Error: Connection failed ({e}). Retrying in 5s...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(ble_run())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Shutting down...")
    except Exception as e:
        print(f"Main program crashed: {e}")