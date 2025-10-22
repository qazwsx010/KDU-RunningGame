#include <Wire.h>
#include <MPU6050.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

MPU6050 mpu;

#define SERVICE_UUID        "12345678-1234-1234-1234-1234567890ab"
#define CHARACTERISTIC_UUID "abcd1234-5678-90ab-cdef-1234567890ab"

BLECharacteristic *pCharacteristic;

// BLE 연결/해제 상태를 시리얼 모니터로 확인하기 위한 콜백 클래스
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      Serial.println("!!! Client Connected (BLE) !!!");
    };

    void onDisconnect(BLEServer* pServer) {
      Serial.println("!!! Client Disconnected - Restarting Advertising !!!");
      BLEDevice::startAdvertising(); 
    }
};


void setup() {
    Serial.begin(115200);
    Wire.begin();

    // MPU6050 초기화
    mpu.initialize();
    if (mpu.testConnection()) {
        Serial.println("MPU6050 OK");
    } else {
        Serial.println("MPU6050 failed");
    }

    // BLE 초기화
    BLEDevice::init("RUNNIG_BOARD_2"); 
    
    BLEServer *pServer = BLEDevice::createServer();
    
    // 서버에 콜백 등록 (연결 상태 확인용)
    pServer->setCallbacks(new MyServerCallbacks()); 
    
    BLEService *pService = pServer->createService(SERVICE_UUID);
    
    pCharacteristic = pService->createCharacteristic(
                            CHARACTERISTIC_UUID,
                            BLECharacteristic::PROPERTY_NOTIFY
                        );
    
    pCharacteristic->addDescriptor(new BLE2902());
    pService->start();
    
    // BLE 광고 설정 강화
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    
    // 장치 이름이 포함된 스캔 응답을 활성화합니다.
    pAdvertising->setScanResponse(true); 
    
    // 광고 데이터에 서비스 UUID를 포함하여 장치 검색을 돕습니다.
    pAdvertising->addServiceUUID(SERVICE_UUID);
    
    pAdvertising->start();
    Serial.println("BLE advertising started with enhanced settings");
}

void loop() {
    static unsigned long lastTime = 0;
    
    if (millis() - lastTime >= 45) { // 45ms
        lastTime = millis();

        int16_t ax, ay, az, gx, gy, gz;
        mpu.getAcceleration(&ax, &ay, &az);
        mpu.getRotation(&gx, &gy, &gz);

        const int16_t SCALE_FACTOR = 4; // 4로 나누어 데이터 크기를 1/4로 줄입니다.

        ax /= SCALE_FACTOR;
        ay /= SCALE_FACTOR;
        az /= SCALE_FACTOR;
        gx /= SCALE_FACTOR;
        gy /= SCALE_FACTOR;
        gz /= SCALE_FACTOR;

        // JSON 문자열 생성
        String jsonStr = "{\"ax\":" + String(ax) + ",\"ay\":" + String(ay) +
                         ",\"az\":" + String(az) + ",\"gx\":" + String(gx) +
                         ",\"gy\":" + String(gy) + ",\"gz\":" + String(gz) + "}";

        // BLE로 전송
        pCharacteristic->setValue(jsonStr.c_str());
        pCharacteristic->notify();

        Serial.println(jsonStr); // 센서 값 확인용
    }
}