import time
import os
from tkinter import Tk, Label, Button, Entry, StringVar, Frame, OptionMenu, messagebox

from otp_core import OTPGenerator

class OTPUI:
    def __init__(self, otp_generator, key_manager):
        """
        OTP UI 초기화
        
        매개변수:
        - otp_generator: OTPGenerator 인스턴스
        - key_manager: KeyManager 인스턴스
        """
        self.otp_generator = otp_generator
        self.key_manager = key_manager
        
        # UI 구성요소
        self.root = Tk()
        self.root.title("OTP 생성기")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 구성요소 설정"""
        # 타이틀
        Label(self.root, text="OTP 생성기", font=("Arial", 18, "bold")).pack(pady=20)
        
        # OTP 표시 영역
        self.otp_frame = Frame(self.root)
        self.otp_frame.pack(pady=10)
        
        self.otp_value = StringVar()
        self.otp_value.set("------")
        
        self.otp_label = Label(self.otp_frame, textvariable=self.otp_value, 
                              font=("Arial", 32, "bold"), width=8)
        self.otp_label.pack()
        
        self.remaining_time = StringVar()
        self.remaining_time.set("남은 시간: 0초")
        
        Label(self.otp_frame, textvariable=self.remaining_time).pack()
        
        # 버튼 영역
        button_frame = Frame(self.root)
        button_frame.pack(pady=20)
        
        # 계정 선택 드롭다운
        self.account_var = StringVar()
        self.update_account_list()
        
        Label(button_frame, text="계정 선택:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.account_menu = OptionMenu(button_frame, self.account_var, "")
        self.account_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # 새 계정 추가 영역
        Label(button_frame, text="새 계정 이름:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.new_account_entry = Entry(button_frame, width=20)
        self.new_account_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        Label(button_frame, text="비밀번호:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = Entry(button_frame, width=20, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # 버튼들
        Button(button_frame, text="계정 추가", command=self.add_account).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        Button(button_frame, text="QR코드 생성", command=self.generate_qr_code).grid(row=3, column=1, padx=5, pady=5, sticky="w")
        Button(button_frame, text="계정 삭제", command=self.delete_account).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        Button(button_frame, text="OTP 생성", command=self.generate_otp).grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # OTP 업데이트 타이머 시작
        self.update_otp()
    
    def update_account_list(self):
        """계정 목록 업데이트"""
        # 기존 메뉴 항목 제거
        menu = self.account_var._nametowidget(self.account_var._name)
        menu['menu'].delete(0, 'end')
        
        # 계정 목록 가져오기
        accounts = self.key_manager.list_keys()
        
        if accounts:
            self.account_var.set(accounts[0])
            for account in accounts:
                menu['menu'].add_command(label=account, command=lambda value=account: self.account_var.set(value))
        else:
            self.account_var.set("계정 없음")
    
    def add_account(self):
        """새 계정 추가"""
        account_name = self.new_account_entry.get().strip()
        password = self.password_entry.get()
        
        if not account_name or not password:
            messagebox.showerror("오류", "계정 이름과 비밀번호를 모두 입력해주세요.")
            return
        
        try:
            self.key_manager.generate_key_from_password(password, account_name)
            messagebox.showinfo("성공", f"'{account_name}' 계정이 추가되었습니다.")
            
            # 입력 필드 초기화 및 계정 목록 업데이트
            self.new_account_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.update_account_list()
            
        except Exception as e:
            messagebox.showerror("오류", f"계정 추가 중 오류가 발생했습니다: {e}")
    
    def delete_account(self):
        """계정 삭제"""
        account_name = self.account_var.get()
        
        if account_name == "계정 없음":
            messagebox.showerror("오류", "삭제할 계정이 없습니다.")
            return
        
        if messagebox.askyesno("확인", f"'{account_name}' 계정을 삭제하시겠습니까?"):
            if self.key_manager.delete_key(account_name):
                messagebox.showinfo("성공", f"'{account_name}' 계정이 삭제되었습니다.")
                self.update_account_list()
            else:
                messagebox.showerror("오류", "계정 삭제 중 오류가 발생했습니다.")
    
    def generate_qr_code(self):
        """QR 코드 생성"""
        account_name = self.account_var.get()
        
        if account_name == "계정 없음":
            messagebox.showerror("오류", "QR 코드를 생성할 계정이 없습니다.")
            return
        
        try:
            qr_path = self.key_manager.generate_qr_code(account_name)
            messagebox.showinfo("성공", f"QR 코드가 생성되었습니다.\n파일: {qr_path}")
            
            # 운영체제에 따라 파일 열기
            if os.name == 'nt':  # Windows
                os.startfile(qr_path)
            elif os.name == 'posix':  # macOS, Linux
                os.system(f"open {qr_path}")
            
        except Exception as e:
            messagebox.showerror("오류", f"QR 코드 생성 중 오류가 발생했습니다: {e}")
    
    def generate_otp(self):
        """OTP 코드 생성"""
        account_name = self.account_var.get()
        
        if account_name == "계정 없음":
            messagebox.showerror("오류", "OTP를 생성할 계정이 없습니다.")
            return
        
        try:
            key, algorithm, digits = self.key_manager.get_key(account_name)
            self.otp_generator = OTPGenerator(key, algorithm, digits)
            otp, remaining = self.otp_generator.generate_totp()
            
            self.otp_value.set(otp)
            self.remaining_time.set(f"남은 시간: {remaining}초")
            
        except Exception as e:
            messagebox.showerror("오류", f"OTP 생성 중 오류가 발생했습니다: {e}")
    
    def update_otp(self):
        """OTP 자동 업데이트"""
        account_name = self.account_var.get()
        
        if account_name != "계정 없음":
            try:
                key, algorithm, digits = self.key_manager.get_key(account_name)
                self.otp_generator = OTPGenerator(key, algorithm, digits)
                otp, remaining = self.otp_generator.generate_totp()
                
                self.otp_value.set(otp)
                self.remaining_time.set(f"남은 시간: {remaining}초")
                
            except Exception:
                self.otp_value.set("------")
                self.remaining_time.set("남은 시간: 0초")
        
        # 1초마다 업데이트
        self.root.after(1000, self.update_otp)
    
    def run(self):
        """UI 실행"""
        self.root.mainloop()