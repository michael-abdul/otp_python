# **OTP 생성기 (Python)**

시간 기반 일회용 비밀번호(TOTP)를 생성하는 파이썬 애플리케이션입니다. 이 프로젝트는 암호화 알고리즘을 활용하여 온라인 서비스의 2단계 인증(2FA)에 사용할 수 있는 보안 코드를 생성합니다.

## **주요 기능**

- **시간 기반 OTP(TOTP) 생성**: RFC 6238 규격에 따른 30초 간격의 OTP 생성
- **다중 계정 관리**: 여러 서비스의 OTP를 한 곳에서 관리
- **비밀번호 기반 키 생성**: 사용자 비밀번호로부터 안전한 OTP 시드 생성
- **모바일 앱 호환**: Google Authenticator 등의 앱과 호환

## **설치 방법**

### **필수 조건**

- Python 3.6 이상
- 가상환경(venv) 사용 권장

### **설치 단계**

1. 저장소 복제 또는 다운로드

   ```bash

   bash
   git clone <repository-url>
   cd otp-python

   ```

2. 가상환경 생성 및 활성화

   ```bash

   bash
   python -m venv .venv
   source .venv/bin/activate# Linux/macOS# 또는# .venv\Scripts\activate  # Windows

   ```

3. 필요한 패키지 설치

   ```bash

   bash
   pip install pycryptodome pillow pyqrcode

   ```

## **사용 방법**

이 프로젝트는 명령줄 인터페이스(CLI)를 통해 사용할 수 있습니다.

### **기본 명령어**

1. 새 계정 추가

   ```bash

   bash
   python main.py --cli --add-account <계정이름> --password <비밀번호>

   ```

2. 계정 목록 확인

   ```bash

   bash
   python main.py --cli --list

   ```

3. OTP 코드 생성 (실시간 업데이트)

   ```bash

   bash
   python main.py --cli --account <계정이름>

   ```

4. 계정 삭제

   ```bash

   bash
   python main.py --cli --delete <계정이름>

   ```

5. QR 코드 생성 (Google Authenticator 앱과 연동)

   ```bash

   bash
   python main.py --cli --generate-qr <계정이름>

   ```

### **예시**

```bash

bash
# Google 계정 추가
python main.py --cli --add-account google --password mysecretpass

# OTP 코드 생성 및 확인
python main.py --cli --account google

```

## **테스트 방법**

다음 단계에 따라 OTP 생성기의 모든 기능을 테스트할 수 있습니다:

1. **계정 추가 테스트**예상 결과: 각 명령어 실행 후 계정 추가 성공 메시지가 표시됩니다.

   ```bash

   bash
   python main.py --cli --add-account google --password mysecretpass
   python main.py --cli --add-account facebook --password anothersecret

   ```

2. **계정 목록 테스트**예상 결과: 추가한 계정 목록(google, facebook)이 표시됩니다.

   ```bash

   bash
   python main.py --cli --list

   ```

3. **OTP 생성 테스트**예상 결과: 6자리 OTP 코드와 남은 시간이 표시되며, 30초마다 코드가 자동으로 갱신됩니다.

   ```bash

   bash
   python main.py --cli --account google

   ```

4. **계정 삭제 테스트**예상 결과: facebook 계정이 삭제되고, 목록에서 google만 표시됩니다.

   ```bash

   bash
   python main.py --cli --delete facebook
   python main.py --cli --list

   ```

5. **모바일 앱 연동 테스트**예상 결과: QR 코드 이미지 파일이 생성됩니다. 이 QR 코드를 Google Authenticator 앱으로 스캔하면 동일한 OTP가 생성되는지 확인합니다.

   ```bash

   bash
   python main.py --cli --generate-qr google

   ```

## **모바일 앱 연동 방법**

1. QR 코드 생성:

   ```bash

   bash
   python main.py --cli --generate-qr <계정이름>

   ```

2. 생성된 QR 코드 이미지 파일을 찾습니다.
3. Google Authenticator, Microsoft Authenticator 또는 Authy와 같은 OTP 앱에서 QR 코드를 스캔합니다.
4. 앱에 표시되는 OTP 코드와 이 프로그램에서 생성된 코드가 일치하는지 확인합니다:

   ```bash

   bash
   python main.py --cli --account <계정이름>

   ```

## **프로젝트 구조**

```

otp-python/
├── main.py            # 메인 실행 파일
├── otp_core.py        # OTP 생성 알고리즘
├── key_manager.py     # 키 관리 모듈
├── ui.py              # GUI 인터페이스 (옵션)
└── otp_keys.json      # 저장된 키 정보

```

## **보안 고려사항**

- OTP 키는 로컬 시스템의 `otp_keys.json` 파일에 저장됩니다.
- 비밀번호 기반 키 생성 시 PBKDF2 알고리즘을 사용하여 보안을 강화합니다.
- 중요한 계정에 사용할 경우, 키 파일을 안전하게 보관하세요.
