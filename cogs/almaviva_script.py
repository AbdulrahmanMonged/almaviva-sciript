from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import requests
import capsolver
import json
from .Document import Document
from .colors import *
from customtkinter import CTkInputDialog
from .Countdown import Countdown
from .sheet_management import *

SIGN_IN_URL = "https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/protocol/openid-connect/auth?response_type=code&client_id=aa-visasys-public&state=dDF5U0ZtZ0VVbDFUT2VVMjlOYXd3SWRvLmVyeUpOVy0zYW9zbV8yYnRNdWll&redirect_uri=https%3A%2F%2Fegy.almaviva-visa.it%2F&scope=openid%20profile%20email&code_challenge=DGqFJkz70cuSjv8tiajECZNahV4AhAhPauxkp3Q4rZc&code_challenge_method=S256&nonce=dDF5U0ZtZ0VVbDFUT2VVMjlOYXd3SWRvLmVyeUpOVy0zYW9zbV8yYnRNdWll"
MAIN_PAGE = "https://egy.almaviva-visa.it/"
capsolver.api_key = "CAP-C00F3CDADDD84311E2252F31AE7CDD42"

class Bot:
    def __init__(self, window, applicant, documents):
        self.window = window
        self.applicant = applicant
        self.documents = documents
        self.accounts = []
        self.token = ""
        self.recaptcha = ""
        self.otp = ""
        self.slots = []
        self.thread_evenet = threading.Event()
        self.session = requests.Session()
        self.driver = None
        self.token_thread = threading.Thread(target=self.get_token)
        self.main_thread_flag = 1
        self.username = ""
        self.password = ""
        self.curr_token = ""
        self.visa_id = 20
        self.count = 0
        self.account_index = 0

    def add_applicant(self, applicant):
        applicant.set_bot(self)
        self.applicant = applicant

    def change_account(self):
        self.window.print_in_log("جاري تغيير الحساب...", color=warning)
        self.count = 0
        self.account_index = (self.account_index + 1) % len(self.applicants)
        self.username = self.applicants[self.account_index][0]
        self.password = self.applicants[self.account_index][1]
        self.window.print_in_log("تم تغيير الحساب", color=success)
        self.driver.close()
        self.login()

    def send_otp(self):
        try:
            self.window.print_in_log("جاري ارسال الكود... OTP", color=warning)
            api_url = "https://egyapi.almaviva-visa.it/reservation-manager//api/otp/v1"
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Origin": "https://egy.almaviva-visa.it",
                "Referer": "https://egy.almaviva-visa.it/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
            }
            data = {}
            response = self.session.post(api_url, headers=headers, json=data)

        except Exception as e:
            self.window.print_in_log("يوجد خطأ في الارسال الكود... OTP", color=danger)

    def get_otp(self):
        self.window.print_in_log("جاري الحصول على الكود... OTP", color=warning)
        otp = CTkInputDialog(text="Enter OTP", title="OTP")
        self.otp = otp.get_input()
        return otp

    def verify_otp(self):
        try:
            self.window.print_in_log(("جاري التحقق من الكود... OTP"), color=warning)
            api_url = f"https://egyapi.almaviva-visa.it/reservation-manager//api/otp/v1/{self.otp}"
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Origin": "https://egy.almaviva-visa.it",
                "Referer": "https://egy.almaviva-visa.it/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
            }
            data = {}
            response = self.session.post(api_url, headers=headers, json=data)
            if response.status_code == 200:
                self.window.print_in_log("تم التحقق من الكود... OTP", color=success)
        except Exception as e:
            self.window.print_in_log("يوجد خطأ في التحقق من الكود... OTP")

    def get_recaptcha(self):
        try:
            self.window.print_in_log("جاري التحقق من كابتشا...", color=warning)
            response = capsolver.solve(
                {
                    "type": "ReCaptchaV2TaskProxyLess",
                    "websiteURL": "https://egy.almaviva-visa.it/appointment",
                    "websiteKey": "6LewmsUpAAAAAOJYsdlzBrXXYzKvMwTqzrw-H-qP",
                    "isInvisible": True,
                }
            )
            self.recaptcha = response["gRecaptchaResponse"]
        except Exception as e:
            self.window.print_in_log("يوجد خطأ في الكابتشا...", color=danger)

    def get_token(self):
        try:
            while not (self.thread_evenet.is_set()):
                self.driver.refresh()
                self.token = self.driver.execute_script(
                    "return window.sessionStorage.getItem('access_token');"
                )
                time.sleep(5)
                if not (self.token):
                    self.driver.get(MAIN_PAGE)
                if self.token:
                    if self.token != self.curr_token:
                        return
                    self.curr_token = self.token
        except Exception as e:
            print(e)
            pass

    def get_available_slots(self):
        try:
            self.window.print_in_log("جاري الحصول على المواعيد...", color=warning)
            api_url = "https://egyapi.almaviva-visa.it/reservation-manager/api/slots/v1/free?officeId=1&quantity=1&date=2024-05-30&type=WEB"
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.token}",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Host": "egyapi.almaviva-visa.it",
                "Origin": "https://egy.almaviva-visa.it",
                "Referer": "https://egy.almaviva-visa.it/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
            }
            response = self.session.get(api_url, headers=headers)
            self.slots = response.json()
        except Exception as e:
            self.window.print_in_log(
                "يوجد خطأ في الحصول على المواعيد... جاري اعادة المحاولة", color=danger
            )

    def check_for_availabilty(self):
        try:
            self.window.print_in_log(("جاري التحقق من المواعيد..."), color=warning)
            api_url = f"https://egyapi.almaviva-visa.it/reservation-manager/api/planning/v1/checks?officeId=1&visaId={self.visa_id}&serviceLevelId=1"
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.token}",
                "Accept-Language": "en",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Connection": "keep-alive",
                "DeviceOperatingSystem": "web",
                "Host": "egyapi.almaviva-visa.it",
                "Origin": "https://egy.almaviva-visa.it",
                "Referer": "https://egy.almaviva-visa.it/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
            }
            response = self.session.get(api_url, headers=headers)
            self.count += 1
            if self.count == 20:
                self.change_account()
                return False
            if response.status_code == 429:
                self.window.print_in_log(
                    "تم تخطي عدد المرات المسموح بها للكشف علي المواعيد جاري انتظر ربع ساعة ثم سيتم اكمال المهمة مرة اخري"
                )
                time.sleep(60 * 15)
                return False
            return response.json()
        except Exception as e:
            self.window.print_in_log(
                "يوجد خطأ في التحقق من المواعيد... جاري اعادة المحاولة", color=danger
            )
            return False

    def get_account_data(self):
        api_url = "https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/protocol/openid-connect/userinfo"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self.token}",
            "Accept-Language": "en",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Connection": "keep-alive",
            "Host": "egyiam.almaviva-visa.it",
            "Origin": "https://egy.almaviva-visa.it",
            "Referer": "https://egy.almaviva-visa.it/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        self.window.print_in_log("جاري تحميل بيانات الحساب", color=warning)
        response = self.session.get(api_url, headers=headers)
        data = {
            "name": response.json()["given_name"],
            "family_name": response.json()["family_name"],
            "email": response.json()["email"],
            "phone": response.json()["phone_number"],
        }
        self.window.print_in_log("تم تحميل بيانات الحساب", color=success)
        self.applicant.set_new_data(data)

    def init_driver(self):
        self.window.print_in_log("جاري تشغيل التطبيق", color=warning)
        option = Options()
        option.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=option)

    def login(self):
        try:
            self.driver.get(SIGN_IN_URL)
            self.window.print_in_log("جاري تسجيل الدخول", color=warning)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            self.driver.find_element(By.ID, "username").send_keys(self.username)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.ID, "kc-login").click()
            self.window.print_in_log("تم تسجيل الدخول", color=success)
            threading.Thread(target=update_login_status, args=("Success",)).start()
        except Exception as e:
            self.window.print_in_log(
                "يوجد خطأ في تسجيل الدخول... جاري اعادة المحاولة", color=danger
            )
            self.driver.close()
            self.login()

    def upload_documents(self):
        self.window.print_in_log("جاري تحميل المستندات...", color=warning)
        for doc in self.documents:
            document = Document(self.documents[doc][1], self.documents[doc][0])
            document.upload_document(self.token)
            self.applicant.add_document(document)
        self.window.print_in_log("تم تحميل المستندات", color=success)

    def start_booking(self):
        try:
            while self.main_thread_flag:
                self.username = self.accounts[self.account_index][0]
                self.password = self.accounts[self.account_index][1]
                self.init_driver()
                self.login()
                self.token_thread.start()
                while not (self.curr_token):
                    pass
                print("TOKEN")
                self.upload_documents()
                countdown = Countdown(9, 0)
                # if countdown.get_remaining_seconds() < 60 * 60 * 19:
                #     self.window.print_in_log("البرنامج سيبدأ الساعة 9 صباحا...", color=warning)
                #     time.sleep(countdown.get_remaining_seconds())
                while not (self.check_for_availabilty()):
                    self.window.print_in_log(
                        "لا يوجد مواعيد متاحة... جاري اعادة المحاولة", color=danger
                    )
                    time.sleep(5)
                self.window.print_in_log("يوجد مواعيد متاحة", color=success)
                self.get_available_slots()
                self.send_otp()
                self.applicant.set_bot(self)
                self.get_account_data()
                self.get_recaptcha()
                for date in self.slots:
                    headers = {
                        "Authorization": f"Bearer {self.token}",
                        "Recaptcha": self.recaptcha,
                        "Accept-Language": "en",
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/plain, */*",
                        "DeviceOperatingSystem": "web",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    }

                    body = {
                        "officeId": 1,
                        "tripDate": "2024-05-30",
                        "tripDestination": "roma",
                        "termandcond": True,
                        "idServiceLevel": 1,
                        "applicants": [self.applicant.get_applicant_json()],
                        "slotStartDate": date,
                        "source": "WEB",
                        "otp": self.otp,
                    }
                    URL = "https://egyapi.almaviva-visa.it/reservation-manager/api/visa-applications/v1/checkout?paymentProvider=MASTERCARD"
                    response = self.session.post(URL, headers=headers, data=json.dumps(body))
                    self.window.print_in_log("جاري الحجز...", color=warning)
                    time.sleep(1)
                    if response.status_code == 201:
                        threading.Thread(
                            target=start_excution, args=(self.username, self.password)
                        ).start()
                        threading.Thread(
                            target=update_operation_status, args=("تم الحجز بنجاح",)
                        ).start()
                        self.window.print_in_log("تم الحجز بنجاح", color=success)
                        session_id = response.json()["sessionId"]
                        self.driver.get(
                            f"https://eu.gateway.mastercard.com/checkout/pay/{session_id}?checkoutVersion=1.0.0"
                        )
                        self.window.print_in_log("رابط بوابة الدفع", color=success)
                        self.window.print_in_log(
                            f"https://eu.gateway.mastercard.com/checkout/pay/{session_id}?checkoutVersion=1.0.0"
                        )
                        self.window.print_in_log("تم انتهاء المهمة بنجاح...", color=success)
                        threading.Thread(
                            target=payment_gate_link,
                            args=(
                                f"https://eu.gateway.mastercard.com/checkout/pay/{session_id}?checkoutVersion=1.0.0",
                            ),
                        ).start()
                        self.thread_evenet.set()
                        self.main_thread_flag = 0
                        self.window.print_in_log("تم ايقاف البرنامج بنجاح", color=success)
                        self.token_thread.join()
                        break
        except Exception as e:
            print(e)
            self.window.print_in_log(f"حدث خطأ في البرنامج جاري اعادة المحاولة", color=danger)
