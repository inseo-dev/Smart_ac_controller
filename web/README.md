# 스마트 에어컨 컨트롤러

Flutter로 개발된 스마트 에어컨 제어 애플리케이션입니다. 사용자 인식과 자동 온도 조절 기능을 통해 개인화된 쾌적한 실내 환경을 제공합니다.

## 주요 기능

- 사용자별 선호 온도 설정
- BLE 주소 기반 사용자 자동 인식
- 실시간 에어컨 상태 모니터링
- AI 기반 자동 온도 조절
- 웹 및 모바일 크로스 플랫폼 지원
- 실시간 데이터 동기화

## 요구사항

- Flutter 3.0.0 이상
- Dart 2.17.0 이상
- Android 6.0 (API level 23) 이상
- iOS 11.0 이상
- 웹 브라우저 (Chrome, Safari, Edge, Firefox 최신 버전)

## 설치 방법

1. 저장소 클론
   ```bash
   git clone https://github.com/your-username/smart-aircon-controller.git
   cd smart-aircon-controller
   ```

2. 의존성 설치
   ```bash
   flutter pub get
   ```

3. 환경 설정
   ```bash
   # 개발 환경 설정 파일 복사
   cp lib/config/server_config.dart.example lib/config/server_config.dart
   ```

4. 서버 주소 설정 (`lib/config/server_config.dart` 수정)
   ```dart
   // 개발 환경
   static const String baseUrl = 'http://your-server-ip:8000';
   
   // 또는 프로덕션 환경
   // static const String baseUrl = 'https://your-production-server.com';
   ```

5. 앱 실행
   ```bash
   # 웹 실행
   flutter run -d chrome
   
   # 안드로이드 실행
   flutter run -d android
   
   # iOS 실행
   flutter run -d ios
   ```

## API 문서

### 사용자 관리

| 메소드 | 엔드포인트 | 설명 |
|--------|------------|------|
| `GET` | `/serv_fr/users` | 사용자 목록 조회 |
| `POST` | `/serv_fr/users` | 새 사용자 추가 |
| `PATCH` | `/serv_fr/users/{id}` | 사용자 정보 수정 |
| `DELETE` | `/serv_fr/users/{id}` | 사용자 삭제 |

### 에어컨 제어

| 메소드 | 엔드포인트 | 설명 |
|--------|------------|------|
| `GET` | `/serv_fr/ac/state` | 에어컨 상태 조회 |
| `POST` | `/serv_fr/ac/control` | 에어컨 제어 |
| `GET` | `/serv_fr/env/target_temp` | 설정 온도 조회 |
| `POST` | `/serv_fr/env/target_temp` | 설정 온도 변경 |

### 사용자 감지

| 메소드 | 엔드포인트 | 설명 |
|--------|------------|------|
| `GET` | `/serv_fr/detections/users` | 감지된 사용자 목록 조회 |

## 사용 방법

1. **에어컨 제어**
   - 메인 화면에서 현재 온도와 설정 온도를 확인합니다.
   - 온도 조절 버튼을 눌러 원하는 온도로 설정합니다.
   - 전원 버튼으로 에어컨을 켜고 끌 수 있습니다.

2. **자동 모드**
   - AI 자동 모드를 활성화하면 사용자 패턴에 따라 자동으로 온도를 조절합니다.
   - 방에 사용자가 감지되면 해당 사용자의 선호 온도로 자동 조정됩니다.

## 데이터 모델

### 사용자 정보
```json
{
  "user_id": 1,
  "user_name": "홍길동",
  "temp_preferred": 25.0,
  "ble_address": "AA:BB:CC:DD:EE:FF",
  "created_at": "2023-01-01T00:00:00Z"
}
```

### 에어컨 상태
```json
{
  "power": true,
  "mode": "cool",
  "current_temp": 28.5,
  "target_temp": 25.0,
  "fan_speed": "medium"
}
```

### 에어컨 상태 구조

```json
{
  "ac_action": "ON",
  "ac_temp": 25
}
```

## 🛠️ 설치 및 실행

### 필수 요구사항

- Flutter SDK 3.7.2+
- Dart SDK 3.0.0+
- Node.js (웹 빌드용)

### 설치

1. **의존성 설치**
   ```bash
   flutter pub get
   ```

2. **JSON 코드 생성**
   ```bash
   flutter packages pub run build_runner build
   ```

3. **웹 실행**
   ```
   bash
   flutter run -d chrome
   ```

### 웹 빌드

```bash
# 최적화된 웹 빌드
flutter build web --release --optimization-level 4 --no-source-maps --web-resources-cdn

# 빌드된 파일 위치
build/web/
```

## 📁 프로젝트 구조

```
lib/
├── config/
│   └── server_config.dart        # 서버 설정
├── models/
│   ├── user.dart               # 사용자 모델
│   ├── ac_state.dart           # 에어컨 상태 모델
│   └── api_response.dart       # API 응답 모델
├── providers/
│   ├── user_provider.dart      # 사용자 상태 관리
│   └── ac_provider.dart        # 에어컨 상태 관리
├── ui/
│   └── home_page.dart          # 메인 UI
└── main.dart                   # 앱 진입점
```

## 🔧 개발 환경 설정

### 1. 서버 연결 테스트

```bash
# 서버 상태 확인
curl http://your-server-ip:8000/serv_fr/users
```

### 2. 서버 URL 변경

```dart
// lib/config/server_config.dart 파일에서
static const String baseUrl = 'http://your-server-ip:8000';
```

### 3. 디버그 모드

```bash
# 디버그 모드로 실행
flutter run --debug

# 로그 확인
flutter logs
```

## 🚀 배포

### 웹 배포

1. **GitHub Pages**
   ```bash
   git add .
   git commit -m "웹 배포 준비 완료"
   git push origin main
   ```

2. **Netlify**
   - `build/web` 폴더를 Netlify에 드래그 앤 드롭

3. **Firebase Hosting**
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase init hosting
   firebase deploy
   ```

## 🐛 문제 해결

### 일반적인 문제

1. **서버 연결 실패**
   - `lib/config/server_config.dart`에서 서버 URL 확인
   - 네트워크 연결 상태 확인

2. **빌드 오류**
   ```bash
   # 의존성 정리
   flutter clean
   flutter pub get
   
   # JSON 코드 재생성
   flutter packages pub run build_runner clean
   flutter packages pub run build_runner build
   ```

3. **웹 성능 문제**
   - `--optimization-level 4` 사용
   - `--no-source-maps` 옵션 추가
   - CDN 리소스 사용
---

**개발자**: 유현민
**버전**: 1.0.0  
**최종 업데이트**: 2025년 8월 20일
