import base64
import hmac
import hashlib
import time
import json
import os
import sys
import argparse
import struct
import random

class OTPGenerator:
    def __init__(self, secret_key, digits=6):
        """
        OTP 생성기 초기화
        
        매개변수:
        - secret_key: 비밀키 (바이트 형태)
        - digits: OTP 자릿수 (기본값 6)
        """
        self.secret_key = secret_key
        self.digits = digits
    
    def generate_hotp(self, counter):
        """
        HMAC 기반 OTP 생성 (RFC 4226)
        
        매개변수:
        - counter: 카운터 값
        
        반환값:
        - OTP 코드 (문자열)
        """
        # 카운터 값을 8바이트 빅엔디안 형식으로 변환
        counter_bytes = struct.pack('>Q', counter)
        
        # HMAC 계산 (표준 라이브러리 사용)
        h = hmac.new(self.secret_key, counter_bytes, hashlib.sha1).digest()
        
        # 동적 자릿수 (Truncation)
        offset = h[-1] & 0x0F
        binary = ((h[offset] & 0x7F) << 24 |
                 (h[offset + 1] & 0xFF) << 16 |
                 (h[offset + 2] & 0xFF) << 8 |
                 (h[offset + 3] & 0xFF))
        
        # OTP 생성
        otp = binary % (10 ** self.digits)
        return str(otp).zfill(self.digits)
    
    def generate_totp(self, time_step=30):
        """
        시간 기반 OTP 생성 (RFC 6238)
        
        매개변수:
        - time_step: 시간 단계 (초 단위, 기본값 30초)
        
        반환값:
        - OTP 코드 (문자열)
        - 남은 시간 (초)
        """
        # 현재 UNIX 시간을 초 단위로 계산
        now = int(time.time())
        
        # 시간 단계로 나누어 카운터 계산
        counter = now // time_step
        
        # HOTP 알고리즘 사용
        otp = self.generate_hotp(counter)
        
        # 현재 OTP의 남은 유효 시간 계산
        remaining_seconds = time_step - (now % time_step)
        
        return otp, remaining_seconds

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
        return os.urandom(length)  # 표준 라이브러리의 os.urandom 사용
    
    def generate_key_from_password(self, password, name, salt=None):
        """
        사용자 비밀번호로부터 OTP 비밀키 생성
        표준 라이브러리 기반 PBKDF2 구현
        
        매개변수:
        - password: 사용자 비밀번호 (문자열)
        - name: 키 이름 (식별자)
        - salt: 솔트 값 (바이트)
        
        반환값:
        - 생성된 비밀키 (바이트)
        """
        if salt is None:
            salt = os.urandom(16)
        
        # 비밀번호를 바이트로 변환
        password_bytes = password.encode('utf-8')
        
        # 표준 라이브러리의 hashlib.pbkdf2_hmac 사용
        key = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000, 20)
        
        # 키 저장
        self.keys[name] = {
            'key': base64.b32encode(key).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8'),
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
        - 자릿수
        """
        if name not in self.keys:
            raise KeyError(f"'{name}' 키를 찾을 수 없습니다.")
        
        key_info = self.keys[name]
        key_bytes = base64.b32decode(key_info['key'])
        
        return key_bytes, key_info.get('digits', 6)
    
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
    
    def generate_qr_data(self, name, issuer='OTPGenerator'):
        """
        OTP 앱 등록을 위한 otpauth URL 생성
        
        매개변수:
        - name: 키 이름
        - issuer: 발급자 이름
        
        반환값:
        - otpauth URL
        """
        if name not in self.keys:
            raise KeyError(f"'{name}' 키를 찾을 수 없습니다.")
        
        key_info = self.keys[name]
        secret = key_info['key']
        
        # otpauth URL 형식 생성
        otpauth_url = f"otpauth://totp/{name}?secret={secret}&issuer={issuer}"
        
        return otpauth_url

def main():
    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(description='OTP 생성기 - CLI 버전')
    parser.add_argument('--account', help='사용할 계정 이름')
    parser.add_argument('--add-account', help='새 계정 추가')
    parser.add_argument('--password', help='계정 비밀번호')
    parser.add_argument('--delete', help='계정 삭제')
    parser.add_argument('--list', action='store_true', help='계정 목록 출력')
    parser.add_argument('--url', help='특정 계정의 otpauth URL 출력')
    
    args = parser.parse_args()
    
    # 키 관리자 초기화
    key_manager = KeyManager()
    
    # 계정 목록 출력
    if args.list:
        accounts = key_manager.list_keys()
        if accounts:
            print("등록된 계정 목록:")
            for i, account in enumerate(accounts, 1):
                print(f"{i}. {account}")
        else:
            print("등록된 계정이 없습니다.")
        return
    
    # 계정 삭제
    if args.delete:
        if key_manager.delete_key(args.delete):
            print(f"'{args.delete}' 계정이 삭제되었습니다.")
        else:
            print(f"'{args.delete}' 계정을 찾을 수 없습니다.")
        return
    
    # 새 계정 추가
    if args.add_account and args.password:
        key_manager.generate_key_from_password(args.password, args.add_account)
        print(f"'{args.add_account}' 계정이 추가되었습니다.")
        return
    
    # otpauth URL 출력
    if args.url:
        try:
            url = key_manager.generate_qr_data(args.url)
            print(f"otpauth URL: {url}")
            print("\n이 URL을 Google Authenticator나 다른 OTP 앱에 직접 입력하여 사용할 수 있습니다.")
        except KeyError:
            print(f"'{args.url}' 계정을 찾을 수 없습니다.")
        return
    
    # OTP 생성
    if args.account:
        try:
            key, digits = key_manager.get_key(args.account)
            otp_generator = OTPGenerator(key, digits)
            otp, remaining = otp_generator.generate_totp()
            
            print(f"\n계정: {args.account}")
            print(f"OTP: {otp}")
            print(f"남은 시간: {remaining}초\n")
            
            # OTP 변경 타이머 - 콘솔에서 남은 시간 보여주기
            try:
                while True:
                    # 매 초마다 업데이트
                    time.sleep(1)
                    otp, remaining = otp_generator.generate_totp()
                    print(f"\r남은 시간: {remaining}초 | OTP: {otp}", end="")
            except KeyboardInterrupt:
                print("\n\nOTP 생성기 종료")
                
        except KeyError:
            print(f"'{args.account}' 계정을 찾을 수 없습니다.")
        return
    
    # 인수가 없으면 도움말 출력
    parser.print_help()

if __name__ == "__main__":
    main()