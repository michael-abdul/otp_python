import sys
import argparse
from otp_core import OTPGenerator
from key_manager import KeyManager

# CLI 모드인지 확인
is_cli_mode = '--cli' in sys.argv

def main():
    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(description='OTP 생성기')
    parser.add_argument('--cli', action='store_true', help='CLI 모드로 실행')
    parser.add_argument('--account', help='사용할 계정 이름')
    parser.add_argument('--add-account', help='새 계정 추가')
    parser.add_argument('--password', help='계정 비밀번호')
    parser.add_argument('--delete', help='계정 삭제')
    parser.add_argument('--generate-qr', help='QR 코드 생성')
    parser.add_argument('--list', action='store_true', help='계정 목록 출력')
    
    args = parser.parse_args()
    
    # 키 관리자 초기화
    key_manager = KeyManager()
    
    # CLI 모드 실행
    if args.cli or is_cli_mode:
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
        
        # QR 코드 생성
        if args.generate_qr:
            try:
                qr_path = key_manager.generate_qr_code(args.generate_qr)
                print(f"QR 코드가 생성되었습니다: {qr_path}")
            except Exception as e:
                print(f"QR 코드 생성 중 오류 발생: {e}")
            return
        
        # OTP 생성
        if args.account:
            try:
                key, algorithm, digits = key_manager.get_key(args.account)
                otp_generator = OTPGenerator(key, digits)
                otp, remaining = otp_generator.generate_totp()
                
                print(f"계정: {args.account}")
                print(f"OTP: {otp}")
                print(f"남은 시간: {remaining}초")
                
                # 실시간 업데이트 시도
                try:
                    import time
                    print("Ctrl+C를 눌러 종료하세요...")
                    while True:
                        time.sleep(1)
                        otp, remaining = otp_generator.generate_totp()
                        print(f"\r남은 시간: {remaining}초 | OTP: {otp}", end="")
                except KeyboardInterrupt:
                    print("\nOTP 생성기 종료")
                
            except KeyError:
                print(f"'{args.account}' 계정을 찾을 수 없습니다.")
            except Exception as e:
                print(f"OTP 생성 중 오류 발생: {e}")
            return
        
        # 인수가 없으면 도움말 출력
        if len(sys.argv) <= 2:
            parser.print_help()
            print("\n사용 예시:")
            print("  python main.py --cli --add-account google --password mysecretpass")
            print("  python main.py --cli --account google")
            print("  python main.py --cli --list")
        return
    
    # GUI 모드로 실행 - UI 가져오기를 여기서 시도
    try:
        from ui import OTPUI
        
        # 기본 OTP 생성기 및 UI 초기화
        default_key = b"DefaultKeyForInitialization"  # 임시 키
        otp_generator = OTPGenerator(default_key)
        
        # UI 실행
        app = OTPUI(otp_generator, key_manager)
        app.run()
    except ImportError as e:
        print("UI 모듈을 가져올 수 없습니다. tkinter가 설치되어 있는지 확인하세요.")
        print("대신 CLI 모드를 사용하세요: python main.py --cli --help")
        print(f"오류 정보: {e}")

if __name__ == "__main__":
    main()