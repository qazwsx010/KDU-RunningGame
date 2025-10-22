import socket
import json
import select
import time

# ----------------- 소켓 통신 설정 -----------------
HOST = '127.0.0.1'
PORT = 65432

client_socket = None
data_buffer = ""
last_data_time = 0.0

# =====================================================
# ✅ 서버 연결 설정
# =====================================================
def setup_client_socket():
    """서버에 연결을 시도하고 성공 시 논블로킹 소켓을 설정합니다."""
    global client_socket, data_buffer, last_data_time

    if client_socket:
        try:
            client_socket.close()
        except Exception:
            pass
        client_socket = None

    data_buffer = ""
    last_data_time = time.time()

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(3)
        client_socket.connect((HOST, PORT))
        client_socket.setblocking(False)

        print(f"✅ 서버에 연결 성공: {HOST}:{PORT}")
        return True
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        client_socket = None
        return False

# =====================================================
# ✅ 서버 데이터 수신
# =====================================================
import json
import select
import time
import socket

# 💡 전역 변수: 클라이언트 코드에서 반드시 전역으로 정의하고 유지해야 합니다.
# ⚠️ 주의: 실제 사용 환경에 맞게 이 변수들이 main 스코프에 선언되어 있어야 합니다.
# client_socket = None 
# data_buffer = ""
# last_data_time = 0.0
last_successful_data = {"speed": 0.0}

def get_player_data():
    print("get_player_data 함수 실행")
    """
    TCP 소켓에서 데이터를 수신하여 \n 기준으로 JSON을 파싱합니다.
    (client_socket, data_buffer, last_data_time, last_successful_data 변수는 전역으로 가정)
    """
    # 전역 변수를 사용하기 위해 선언
    global client_socket, data_buffer, last_data_time, last_successful_data
    
    # 📌 1. 연결 상태 확인
    if client_socket is None:
        print("[DEBUG] 소켓 연결이 확인되지 않아 초기값을 반환합니다.")
        return last_successful_data # 연결 없음 -> 마지막 성공 데이터 반환

    try:
        # 2. 데이터 읽기 및 버퍼에 추가
        while True:
            ready_to_read, _, _ = select.select([client_socket], [], [], 0.001)
            if not ready_to_read:
                break
            
            try:
                chunk = client_socket.recv(1024)
            except BlockingIOError:
                break
                
            if not chunk:
                # 서버에서 연결이 정상적으로 종료된 경우
                print("[INFO] 서버가 연결을 닫았습니다.")
                client_socket.close()
                client_socket = None
                break
                
            data_buffer += chunk.decode("utf-8")
            last_data_time = time.time()
        
        
        # 📌 3. 버퍼 상태 출력 (수신된 데이터 확인)
        if data_buffer:
            print(f"[RAW BUFFER] 현재 버퍼 내용: {repr(data_buffer)}")

        # 4. '\n' 기준으로 모든 JSON 처리
        results = []
        
        while "\n" in data_buffer:
            json_line, data_buffer = data_buffer.split("\n", 1)
            
            if not json_line.strip():
                continue
                
            try:
                # JSON 문자열을 딕셔너리로 변환
                data = json.loads(json_line)
                results.append(data)
                
                # 🌟 성공적으로 파싱된 데이터를 전역 변수에 저장
                last_successful_data = data 
                
            except json.JSONDecodeError as e:
                # 💡 JSON 디코딩 실패 시 (데이터 손상 또는 불완전)
                print(f"[ERROR/JSON] JSON 디코딩 실패. 오류: {e}, 라인: {repr(json_line.strip())}")
                # 디코딩 실패 라인은 버려지고, data_buffer에는 남은 불완전한 데이터만 남습니다.
                

        # 5. 결과 반환 및 디버깅
        if results:
            # 새로운 결과가 있다면 최신 데이터 반환
            print(f"[client] 반환 성공 : {results}")
            return results[-1]
        else:
            # 💡 results가 비었지만 data_buffer에 데이터가 남아있는 경우:
            if data_buffer:
                print(f"[DEBUG] results는 비었지만 버퍼에 데이터({len(data_buffer)} 바이트)가 남아있음. 다음 호출에서 처리될 예정: {repr(data_buffer[:50])}...")
            
            # 🌟 새로운 데이터 수신에는 실패했으나, 
            # 🌟 마지막으로 성공했던 데이터를 반환하여 안정적인 값 흐름을 유지합니다.
            print(f"[client] 새로운 데이터 없음. 마지막 성공 데이터 반환: {last_successful_data}")
            return last_successful_data 

    except Exception as e:
        print(f"[UNKNOWN ERROR/SPEED] 예외: {e}")
        # 예외 발생 시 소켓 정리 (원래 코드와 동일)
        if client_socket:
            client_socket.close()
            client_socket = None
        # 예외 발생 시에도 마지막 성공 데이터를 반환하여 갑작스러운 값 변경을 방지
        return last_successful_data


def get_client_socket():
    return client_socket


def close_client_socket():
    """클라이언트 소켓 안전하게 닫기"""
    global client_socket
    if client_socket:
        try:
            client_socket.close()
        except Exception:
            pass
        client_socket = None


# =====================================================
# ✅ 독립 실행용
# =====================================================
if __name__ == "__main__":
    if not setup_client_socket():
        exit(1)

    print("🔄 서버 데이터 수신 시작. Ctrl+C로 종료")
    try:
        while True:
            data = get_player_data()
            # data가 None이면 아직 JSON 완성 안 됨
            time.sleep(0.05)  # 50ms 간격
    except KeyboardInterrupt:
        print("\n🛑 종료 요청. 클라이언트 소켓 닫는 중...")
        if client_socket:
            client_socket.close()
