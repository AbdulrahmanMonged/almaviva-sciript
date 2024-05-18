import time
import threading
import requests
import capsolver
import json
from .Document import Document
from .colors import *
from customtkinter import CTkInputDialog
from .Authenticator import Authenticator
from .sheet_management import *
import webbrowser
from .utility import rotate_proxy
from . import secretvars
from .Countdown import Countdown
import time
import aiohttp
from aiohttp_socks import ProxyConnector
import asyncio


SIGN_IN_URL = "https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/protocol/openid-connect/auth?response_type=code&client_id=aa-visasys-public&state=dDF5U0ZtZ0VVbDFUT2VVMjlOYXd3SWRvLmVyeUpOVy0zYW9zbV8yYnRNdWll&redirect_uri=https%3A%2F%2Fegy.almaviva-visa.it%2F&scope=openid%20profile%20email&code_challenge=DGqFJkz70cuSjv8tiajECZNahV4AhAhPauxkp3Q4rZc&code_challenge_method=S256&nonce=dDF5U0ZtZ0VVbDFUT2VVMjlOYXd3SWRvLmVyeUpOVy0zYW9zbV8yYnRNdWll"
MAIN_PAGE = "https://egy.almaviva-visa.it/"
capsolver.api_key = "CAP-C00F3CDADDD84311E2252F31AE7CDD42"


class Bot:
    def __init__(
        self,
        window,
        applicant,
        documents,
        office_id=1,
        visa_id=3,
        mode=0,
        serviceLevel=1,
        countdown=0,
    ):
        self.window = window
        self.applicant = applicant
        self.documents = documents
        self.accounts = []
        self.token = ""
        self.recaptcha = ""
        self.otp = ""
        self.slots = []
        self.session = requests.Session()
        self.driver = None
        self.main_thread_flag = 1
        self.username = ""
        self.password = ""
        self.visa_id = visa_id
        self.office_id = 1 if office_id == "Cairo" else 2
        self.proxy = rotate_proxy()
        self.payment_link = ""
        self.mode = mode
        self.availability = False
        self.serviceLevel = serviceLevel
        self.countdown = countdown
        self.tokens = []
        self.FLAG = 1
        self.threads = []
        self.booked = 0

    def add_applicant(self, applicant):
        applicant.set_bot(self)
        self.applicant = applicant

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
            response = self.session.post(
                api_url, headers=headers, json=data, proxies=self.proxy
            )
            if response.status_code == 200:
                self.window.print_in_log("تم التحقق من الكود... OTP", color=success)
        except Exception as e:
            self.window.print_in_log("يوجد خطأ في التحقق من الكود... OTP")

    async def get_recaptcha(self):
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
            print(e)
            self.window.print_in_log("يوجد خطأ في الكابتشا...", color=danger)

    def write_payment_link(self, payment_link=None, token=None):
        if not payment_link:
            payment_link = self.payment_link
        if not token:
            token = self.token
            
        user = self.get_user(token)[0] if not(self.username) else self.username
        webbrowser.open(
            f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0"
        )
        self.window.print_in_log("رابط بوابة الدفع", color=success)
        self.window.print_in_log(
            f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0",
            color=success,
            url=f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0",
        )
        self.window.print_in_log("تم انتهاء المهمة بنجاح...", color=success)
        threading.Thread(
            target=payment_gate_link,
            args=(
                f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0",
            ),
        ).start()
        with open("payment_link.txt", "a+") as f:
            f.write(
                f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0 - {user}\n"
            )

    def login(self):
        self.window.print_in_log("جاري تسجيل الدخول...", color=warning)
        auth = Authenticator(window=self.window, proxies=self.proxy)
        self.token = auth.login_and_get_token(self.username, self.password)
        if not (auth.login_permission):
            if len(self.accounts) > 1:
                self.change_account()
            else:
                self.window.print_in_log(
                    "عذرا يوجد مستخدم واحد فقط لذلك سيتوقف البرنامج", color=danger
                )
                self.main_thread_flag = 0
                secretvars.MAIN_FLAG = 0

    def check_connection(self):
        try:
            return self.session.get(SIGN_IN_URL).status_code
        except Exception as e:
            return 400

    def collect_tokens(self):
        for account in self.accounts:
            auth = Authenticator(window=self.window, proxies=rotate_proxy())
            token = auth.login_and_get_token(account[0], account[1])
            if not (auth.login_permission):
                self.accounts.remove(account)
                continue
            self.tokens.append(token)

    def get_user(self, token):
        return self.accounts[self.tokens.index(token)]

    async def async_get_available_slots(self, session, token):
        try:
            self.window.print_in_log("جاري الحصول علي اماكن للحجز", color=warning)
            api_url = f"https://egyapi.almaviva-visa.it/reservation-manager/api/slots/v1/free?officeId={self.office_id}&quantity=1&date=2024-06-30&type=WEB"
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {token}",
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
            response = await session.get(api_url, headers=headers)
            self.window.print_in_log("تم الحصول علي اماكن للحجز", color=success)
            return await response.json()
        except Exception as e:
            print(e)
            self.window.print_in_log("يوجد خطأ في الحصول علي اماكن للحجز", color=danger)

    async def async_send_otp(self, session, token):
        try:
            self.window.print_in_log("جاري ارسال الكود... OTP", color=warning)
            api_url = "https://egyapi.almaviva-visa.it/reservation-manager//api/otp/v1"
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {token}",
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
            response = await session.post(
                api_url,
                headers=headers,
                data=json.dumps(data),
            )
            self.window.print_in_log("تم ارسال الكود... OTP", color=success)
        except Exception as e:
            self.window.print_in_log("يوجد خطأ في الارسال الكود... OTP", color=danger)

    async def async_upload_documents(self, session, token):
        self.window.print_in_log("جاري تحميل المستندات...", color=warning)
        for doc in self.documents:
            document = Document(self.documents[doc][1], self.documents[doc][0])
            await document.async_upload_document(session, token)
            self.applicant.add_document(document)
        self.window.print_in_log("تم تحميل المستندات", color=success)

    async def async_get_account_data(self, session, token):
        api_url = "https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/protocol/openid-connect/userinfo"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {token}",
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
        response = await session.get(api_url, headers=headers)
        recieved_data = await response.json()
        data = {
            "name": recieved_data["given_name"],
            "family_name": recieved_data["family_name"],
            "email": recieved_data["email"],
            "phone": recieved_data["phone_number"],
        }
        self.window.print_in_log("تم تحميل بيانات الحساب", color=success)
        self.applicant.set_new_data(data)

    async def async_book(self, slot, session, token):
        user = self.get_user(token)[0] if not(self.username) else self.username
        headers = {
            "Authorization": f"Bearer {token}",
            "Recaptcha": self.recaptcha,
            "Accept-Language": "en",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "DeviceOperatingSystem": "web",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        body = {
            "officeId": self.office_id,
            "tripDate": "2024-06-30",
            "tripDestination": "roma",
            "termandcond": True,
            "idServiceLevel": self.serviceLevel,
            "applicants": [self.applicant.get_applicant_json()],
            "slotStartDate": slot,
            "source": "WEB",
            "otp": self.otp,
        }
        URL = "https://egyapi.almaviva-visa.it/reservation-manager/api/visa-applications/v1/checkout?paymentProvider=MASTERCARD"
        response = await session.post(URL, headers=headers, data=json.dumps(body))
        self.window.print_in_log("جاري الحجز...", color=warning)
        print(response.status, await response.text())
        if response.status == 201:
            self.booked = 1
            threading.Thread(
                target=start_excution, args=(user[0], user[1])
            ).start()
            threading.Thread(target=update_login_status, args=("جاري الحجز...",))
            threading.Thread(
                target=update_operation_status, args=("تم الحجز بنجاح",)
            ).start()
            self.window.print_in_log("تم الحجز بنجاح", color=success)
            data = await response.json()
            self.payment_link = data["sessionId"]
            self.main_thread_flag = 0
            secretvars.MAIN_FLAG == 0
            return data["sessionId"]

    async def async_after_confirmation(self, session, token):
        tasks = [
            self.async_get_available_slots(session, token),
            self.async_get_account_data(session, token),
            self.async_send_otp(session, token),
            self.async_upload_documents(session, token),
            self.get_recaptcha()
        ]
        if self.availability and (not self.booked):
            responses = await asyncio.gather(*tasks)
            slots = responses[0]
            self.applicant.set_bot(self)
            for date in slots:
                if self.booked:
                    return
                payment_link = await self.async_book(
                    slot=date, session=session, token=token
                )
                if payment_link:
                    self.write_payment_link(payment_link)
                if self.main_thread_flag == 0 or secretvars.MAIN_FLAG == 0:
                    return
        else:
            self.window.print_in_log(
                "عذرا لا يوجد مواعيد متاحة للحجز...برجاء المحاولة مرة اخري",
                color=danger,
            )

    async def async_check_for_availabilty(self, token):
        user = self.get_user(token)[0] if not(self.username) else self.username
        checking_FLAG = 1
        api_url = f"https://egyapi.almaviva-visa.it/reservation-manager/api/planning/v1/checks?officeId={self.office_id}&visaId={self.visa_id}&serviceLevelId={self.serviceLevel}"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {token}",
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
        try:
            connector = ProxyConnector.from_url(rotate_proxy(True))
            async with aiohttp.ClientSession(connector=connector) as session:
                while (
                    self.FLAG
                    and self.main_thread_flag
                    and secretvars.MAIN_FLAG
                    and checking_FLAG
                ):
                    tasks = [session.get(api_url, headers=headers) for _ in range(2)]
                    responses = await asyncio.gather(*tasks)
                    for response in responses:
                        if not (checking_FLAG):
                            break
                        print(
                            f"{datetime.now().strftime('%H:%M:%S:%f')} - Result of checking is '{(await response.text()).upper()}' Status code: '{response.status}' for user '{user}'"
                        )
                        if response.status == 200:
                            if await response.text() == "true":
                                self.window.print_in_log(
                                f"تم الحصول علي مواعيد للمستخدم ... {user}", color=success
                            )
                                self.availability = True
                                self.FLAG = 0
                                if not self.token or self.username:
                                    self.token = token
                                    await self.async_after_confirmation(
                                        session=session, token=token
                                    )
                                    return
                            else:
                                if not(self.mode):
                                    return
                                await asyncio.sleep(0.1)
                        if response.status == 429:
                            self.window.print_in_log(
                                f"لا يوجد مواعيد للمستخدم حاليا... {user}", color=danger
                            )
                            checking_FLAG = 0
        except Exception as e:
            print(e)

    async def async_run_tasks(self):
        tasks = []
        try:
            self.collect_tokens()
            for token in self.tokens:
                tasks.append(asyncio.create_task(self.async_check_for_availabilty(token)))
            await asyncio.gather(*tasks)
        except Exception as e:
            print(e)
            
    def start_booking(self):
        try:
            if self.mode:
                asyncio.run(self.async_run_tasks())
                
            else:
                if not (self.username) or not (self.password):
                    self.username = self.accounts[0][0]
                    self.password = self.accounts[0][1]
                self.login()
                if self.countdown:
                    countdown = Countdown(8, 59, 59)
                    self.window.print_in_log(
                        f"في انتظار الساعة {countdown} للاستعلام عن المواعيد",
                        color=warning,
                    )
                    time.sleep(countdown.get_remaining_seconds())
                asyncio.run(self.async_check_for_availabilty(self.token))
            if self.main_thread_flag == 0 or secretvars.MAIN_FLAG == 0:
                self.window.print_in_log("تم ايقاف البرنامج بنجاح", color=success)
            else:
                self.window.print_in_log("تم انهاء البرنامج بنجاح لانتهاء جميع الحسابات من الوظيفة", color=success)
        except Exception as e:
            print(e)
            self.window.print_in_log(
                f"حدث خطأ في البرنامج جاري اعادة المحاولة", color=danger
            )
            while True:
                if self.check_connection() == 200:
                    break
                else:
                    self.window.print_in_log(
                        f"يوجد مشكلة بالموقع حاليا... برجاء الانتظار حتي تتم معالجة المشكلة",
                        color=danger,
                    )
                time.sleep(5)
            self.start_booking()
            self.window.print_in_log(
                f"حدث خطأ في البرنامج جاري اعادة المحاولة", color=danger
            )
