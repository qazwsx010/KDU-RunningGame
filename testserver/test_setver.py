import socket
import time
import threading
import json

# =====================================================================
# 🚀 설정 상수 (최대 속도만 남김)
# =====================================================================


TARGET_MAX_SPEED = 4.5 #플레이어속도 여기서 설정


# =====================================================================
# 🚀 설정 상수 (최대 속도만 남김)
# =====================================================================


TCP_HOST = '127.0.0.1'
TCP_PORT = 65432        
MAX_TCP_CONNECTIONS = 1
TCP_SEND_INTERVAL_MS = 50

tcp_clients = [] 

def tcp_server_thread():
    """TCP 서버를 실행하고 TARGET_MAX_SPEED 값을 고정적으로 전송합니다."""
    global tcp_clients
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((TCP_HOST, TCP_PORT))
        server_socket.listen(MAX_TCP_CONNECTIONS)
        print(f"\n✅ TCP Server listening on {TCP_HOST}:{TCP_PORT}")
    except Exception as e:
        print(f"❌ TCP Error: Failed to start server: {e}")
        return

    def accept_clients():
        while True:
            try:
                server_socket.settimeout(0.5) 
                client_conn, addr = server_socket.accept()
                
                if len(tcp_clients) >= MAX_TCP_CONNECTIONS:
                    client_conn.close()
                    continue
                    
                tcp_clients.append(client_conn)
                print(f"🎉 TCP: Client connected from {addr}. Total: {len(tcp_clients)}")
            except socket.timeout:
                continue
            except Exception:
                break 
    
    threading.Thread(target=accept_clients, daemon=True).start()

    speed_to_send = TARGET_MAX_SPEED
    data_to_send = {"speed": speed_to_send}
    message = json.dumps(data_to_send) + '\n' 
    
    while True:
        time.sleep(TCP_SEND_INTERVAL_MS / 1000.0) 
        
        if not tcp_clients:
            continue
            
        print(f"TCP -> Fixed Speed Transmitting: {speed_to_send:.4f}")
        
        clients_to_remove = []
        for client_conn in tcp_clients:
            try:
                client_conn.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"[SERVER_SEND_ERROR] 클라이언트 전송 중 예외 발생: {e}")
                clients_to_remove.append(client_conn)
                
        for client_conn in clients_to_remove:
            tcp_clients.remove(client_conn)
            client_conn.close()
            print(f"TCP: Client disconnected. Total: {len(tcp_clients)}")


if __name__ == "__main__":
    try:
        print(f"🚀 고정 속도 테스트 서버 시작. 전송 속도: {TARGET_MAX_SPEED} | 전송 주기: {TCP_SEND_INTERVAL_MS}ms")
        tcp_server_thread()
    except KeyboardInterrupt:
        print("\n🛑 프로그램 종료 요청. 서버를 닫는 중...")
    except Exception as e:
        print(f"❌ 메인 서버 실행 중 오류 발생: {e}")