import base64
import os
import json
import qrcode
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

class KeyManager:
    def __init__(self, storage_file='otp_keys.json'):
        """
        키 관리자 초기화
        
        매개변수:
        - storage_file: 키 저장 파일 경로
        """
        self.storage_file = storage_file
        self.keys = {}
        self.load_keys()
    
    def generate_random_key(self, length=16):
        """
        난수 비밀키 생성
        
        매개변수:
        - length: 키 길이 (바이트)
        
        반환값:
        - 생성된 비밀키 (바이트)
        """
        return get_random_bytes(length)
    
    def generate_key_from_password(self, password, name, salt=None):
        """
        사용자 비밀번호로부터 OTP 비밀키 생성
        PDF의 PBKDF2 예제 활용
        
        매개변수:
        - password: 사용자 비밀번호 (문자열)
        - name: 키 이름 (식별자)
        - salt: 솔트 값 (바이트)
        
        반환값:
        - 생성된 비밀키 (바이트)
        """
        if salt is None:
            salt = get_random_bytes(16)
        
        # 비밀번호를 바이트로 변환
        password_bytes = password.encode('utf-8')
        
        # PBKDF2를 사용하여 키 생성 (PDF 5장 패스워드기반 키생성 활용)
        key = PBKDF2(password_bytes, salt, dkLen=20, count=1000000, hmac_hash_module=SHA256)
        
        # 키 저장
        self.keys[name] = {
            'key': base64.b32encode(key).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8'),
            'algorithm': 'SHA1',
            'digits': 6
        }
        self.save_keys()
        
        return key
    
    def get_key(self, name):
        """
        저장된 키 가져오기
        
        매개변수:
        - name: 키 이름
        
        반환값:
        - 비밀키 (바이트)
        - 알고리즘
        - 자릿수
        """
        if name not in self.keys:
            raise KeyError(f"'{name}' 키를 찾을 수 없습니다.")
        
        key_info = self.keys[name]
        key_bytes = base64.b32decode(key_info['key'])
        
        return key_bytes, key_info['algorithm'], key_info['digits']
    
    def list_keys(self):
        """
        저장된 모든 키 이름 반환
        
        반환값:
        - 키 이름 목록
        """
        return list(self.keys.keys())
    
    def delete_key(self, name):
        """
        키 삭제
        
        매개변수:
        - name: 삭제할 키 이름
        """
        if name in self.keys:
            del self.keys[name]
            self.save_keys()
            return True
        return False
    
    def save_keys(self):
        """키를 파일에 저장"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.keys, f)
        except Exception as e:
            print(f"키 저장 중 오류 발생: {e}")
    
    def load_keys(self):
        """파일에서 키 로드"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.keys = json.load(f)
        except Exception as e:
            print(f"키 로드 중 오류 발생: {e}")
    
    def generate_qr_code(self, name, issuer='OTPGenerator'):
        """
        OTP 앱 등록을 위한 QR 코드 생성
        
        매개변수:
        - name: 키 이름
        - issuer: 발급자 이름
        
        반환값:
        - QR 코드 이미지 파일 경로
        """
        if name not in self.keys:
            raise KeyError(f"'{name}' 키를 찾을 수 없습니다.")
        
        key_info = self.keys[name]
        secret = key_info['key']
        
        # otpauth URL 형식 생성
        otpauth_url = f"otpauth://totp/{name}?secret={secret}&issuer={issuer}"
        
        # QR 코드 이미지 생성
        img = qrcode.make(otpauth_url)
        
        # 이미지 저장
        file_path = f"{name}_qrcode.png"
        img.save(file_path)
        
        return file_path