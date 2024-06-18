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
from .utility import rotate_proxy, resource_path
from . import secretvars
from .Countdown import Countdown
import aiohttp
from aiohttp_socks import ProxyConnector
import asyncio
from awesometkinter.bidirender import render_text


SIGN_IN_URL = "https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/protocol/openid-connect/auth?response_type=code&client_id=aa-visasys-public&state=dDF5U0ZtZ0VVbDFUT2VVMjlOYXd3SWRvLmVyeUpOVy0zYW9zbV8yYnRNdWll&redirect_uri=https%3A%2F%2Fegy.almaviva-visa.it%2F&scope=openid%20profile%20email&code_challenge=DGqFJkz70cuSjv8tiajECZNahV4AhAhPauxkp3Q4rZc&code_challenge_method=S256&nonce=dDF5U0ZtZ0VVbDFUT2VVMjlOYXd3SWRvLmVyeUpOVy0zYW9zbV8yYnRNdWll"
MAIN_PAGE = "https://egy.almaviva-visa.it/"
capsolver.api_key = "CAP-C00F3CDADDD84311E2252F31AE7CDD42"
api_key = "cb868b0bd38465e0a6ff51525edcf799"

with open(resource_path("open_id_config.json")) as f:
    open_id_config = json.load(f)

with open(resource_path("config.json")) as f:
    config = json.load(f)


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
        otp="",
    ):
        self.window = window
        self.applicant = applicant
        self.documents = documents
        self.accounts = []
        self.token = ""
        self.recaptcha = ""
        self.otp = otp
        self.slots = []
        self.main_thread_flag = 1
        self.username = ""
        self.password = ""
        self.visa_id = visa_id
        self.office_id = 1 if office_id == "Cairo" else 2
        self.payment_link = ""
        self.mode = mode
        self.availability = False
        self.serviceLevel = serviceLevel
        self.countdown = countdown
        self.FLAG = 1
        self.booked = 0
        self.target_h = 8
        self.target_min = 59
        self.target_sec = 54
        self.copied_documents = self.documents
        self.logged_users = {}

        with open(resource_path("open_id_config.json")) as f:
            self.open_id_config = json.load(f)

        with open(resource_path("config.json")) as f:
            self.config = json.load(f)

    def add_applicant(self, applicant):
        applicant.set_bot(self)
        self.applicant = applicant

    def wait_for_otp(self):
        xdxdxdxd = CTkInputDialog(
            text=render_text(
                f"سوف يتم ارسال كود التحقق الي الرقم {self.applicant.get_phone_number()} برجاء الضغط علي Okay لارساله"
            ),
            title="OTP",
        )
        nonsense = xdxdxdxd.get_input()

    def get_otp(self):
        self.window.print_in_log("جاري الحصول على الكود... OTP", color=warning)
        otp = CTkInputDialog(text="Enter OTP", title="OTP")
        self.otp = otp.get_input()

    def get_another_passport(self):
        self.window.print_in_log(
            "الباسبورت مربوط بمستخدم اخر برجاء اضافة باسبورت جديد", color=danger
        )
        passport = CTkInputDialog(
            text=render_text(
                "قم بوضع رقم باسبورت جديد لان الرقم الحالي مربوط بمستخدم اخر"
            ),
            title="Passport",
        )
        self.applicant.set_passport_number(passport.get_input())

    async def verify_otp(self, session):
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
            response = await session.post(
                api_url,
                headers=headers,
                data=json.dumps(data),
            )
            if response.status == 200:
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
            self.window.print_in_log("تم التحقق من الكابتشا بنجاح", color=success)
        except Exception as e:
            print(e)
            self.window.print_in_log("يوجد خطأ في الكابتشا...", color=danger)

    def write_payment_link(self, payment_link=None):
        if not payment_link:
            payment_link = self.payment_link
        with open("payment_link.txt", "a+") as f:
            f.write(
                f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0 - {self.username}\n"
            )
        self.window.print_in_log("رابط بوابة الدفع", color=success)
        self.window.print_in_log(
            f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0",
            color=success,
            url=f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0",
        )
        self.window.print_in_log("تم انتهاء المهمة بنجاح...", color=success)
        webbrowser.open(
            f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0"
        )
        threading.Thread(
            target=lambda: asyncio.run(
                db.finish_excution(
                    self.username,
                    self.password,
                    f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0",
                )
            )
        ).start()

    async def async_get_available_slots(self, session):
        try:
            self.window.print_in_log("جاري الحصول علي اماكن للحجز", color=warning)
            api_url = f"https://egyapi.almaviva-visa.it/reservation-manager/api/slots/v1/free?officeId={self.office_id}&quantity=1&date=2024-06-30&type=WEB"
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
            response = await session.get(api_url, headers=headers)
            self.window.print_in_log("تم الحصول علي اماكن للحجز", color=success)
            result = await response.json()
            print(
                f"{datetime.now().strftime('%H:%M:%S:%f')} - Result of AVAILABLE SLOTS: {result}"
            )
            return result
        except Exception as e:
            print("SLOTS ERROR ", e)
            self.window.print_in_log("يوجد خطأ في الحصول علي اماكن للحجز", color=danger)

    async def async_send_otp(self, session):
        try:
            self.wait_for_otp()
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
            response = await session.post(
                api_url,
                headers=headers,
            )
            if response.status == 200:
                self.window.print_in_log("تم ارسال الكود... OTP", color=success)
                result = await response.json()
                print(
                    f"{datetime.now().strftime('%H:%M:%S:%f')} - Result of OTP sent: {result}"
                )
                self.get_otp()
                await self.verify_otp(session)
            elif response.status == 401:
                await self.async_login_handler(
                    [self.username, self.password], regenerate_token=True
                )
                await self.async_send_otp(session)
        except Exception as e:
            print("OTP ERROR: ", e)
            self.window.print_in_log("يوجد خطأ في الارسال الكود... OTP", color=danger)

    async def async_upload_documents(self, session):
        self.window.print_in_log("جاري تحميل المستندات...", color=warning)
        for doc in self.documents:
            document = Document(self.documents[doc][1], self.documents[doc][0])
            await document.async_upload_document(session, self.token)
            self.applicant.add_document(document)
        self.window.print_in_log("تم تحميل المستندات", color=success)

    async def async_get_account_data(self, session):
        try:
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
        except Exception as e:
            print(e)
            self.window.print_in_log("يوجد خطأ في تحميل بيانات الحساب", color=danger)

    async def async_book(self, slot, session):
        try:
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
            result = await response.json()
            if response.status == 201:
                self.booked = 1
                self.window.print_in_log("تم الحجز بنجاح", color=success)
                data = await response.json()
                self.payment_link = data["sessionId"]
                self.main_thread_flag = 0
                secretvars.MAIN_FLAG = 0
                return data["sessionId"]
            elif response.status == 400:
                if self.main_thread_flag == 0 or secretvars.MAIN_FLAG == 0:
                    return None
                if "Document" in result["message"]:
                    self.window.print_in_log(
                        "يوجد خطا في تحمييل المستندات....جاري اعادة محاولة رفع المستندات",
                        color=danger,
                    )
                    self.documents = self.copied_documents
                    self.applicant.remove_documents()
                    await self.async_upload_documents(session)
                    return await self.async_book(slot, session)
                if "captcha" in result["message"].lower():
                    self.window.print_in_log(
                        "تم انتهاء الكابتشا...جاري حل الكابشتا من جديد", color=danger
                    )
                    await self.get_recaptcha()
                    return await self.async_book(slot, session)
                if "Passport" in result["message"]:
                    self.get_another_passport()
                    return await self.async_book(slot, session)
        except Exception as e:
            print("BOOKING ERROR", e)
            return None

    async def async_after_confirmation(self):
        try:
            connector = ProxyConnector.from_url(rotate_proxy(True))
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [
                    self.async_get_available_slots(session),
                    self.async_get_account_data(session),
                    self.async_upload_documents(session),
                    self.get_recaptcha(),
                ]
                if self.availability and (not self.booked):
                    responses = await asyncio.gather(*tasks)
                    if not self.otp:
                        await self.async_send_otp(session),
                    slots = responses[0]
                    self.applicant.set_bot(self)

                    for date in slots:
                        if self.booked:
                            return
                        await self.async_book(slot=date, session=session)
                        if self.payment_link:
                            self.write_payment_link(self.payment_link)
                        if self.main_thread_flag == 0 or secretvars.MAIN_FLAG == 0:
                            return
                else:
                    self.window.print_in_log(
                        "عذرا لا يوجد مواعيد متاحة للحجز...برجاء المحاولة مرة اخري",
                        color=danger,
                    )
        except Exception as e:
            print(e)
            if self.main_thread_flag == 0 or secretvars.MAIN_FLAG == 0:
                return
            await self.async_after_confirmation()

    async def async_check_for_availabilty(self, user, token):
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
                if self.countdown:
                    countdown = Countdown(
                        self.target_h, self.target_min, self.target_sec
                    )
                    await asyncio.sleep(countdown.get_remaining_seconds())
                print(f"TARGET TIME REACHED - {datetime.now().strftime('%H:%M:%S:%f')}")
                while (
                    self.FLAG
                    and self.main_thread_flag
                    and secretvars.MAIN_FLAG
                    and checking_FLAG
                ):
                    tasks = [session.get(api_url, headers=headers) for _ in range(1)]
                    responses = await asyncio.gather(*tasks)
                    response = responses[0]
                    if not (checking_FLAG):
                        break
                    print(
                        f"{datetime.now().strftime('%H:%M:%S:%f')} - Result of checking is '{(await response.text()).upper()}' Status code: '{response.status}' for user '{user}'"
                    )
                    if response.status == 200:
                        if await response.text() == "true":
                            self.window.print_in_log(
                                f"تم الحصول علي مواعيد للمستخدم ... {user}",
                                color=success,
                            )
                            self.username = user
                            self.token = token
                            self.password = self.logged_users[user][0]
                            return
                        else:
                            if not (self.mode):
                                break
                            await asyncio.sleep(0.1)
                    if response.status == 429:
                        self.window.print_in_log(
                            f"لا يوجد مواعيد للمستخدم حاليا... {user}", color=danger
                        )
                        checking_FLAG = 0
                    if int(response.status) in range(400, 500):
                        checking_FLAG = 0
                await asyncio.sleep(30)

        except Exception as e:
            print("Cheking for availabilty ERROR: ", e)
            await self.async_check_for_availabilty(user, token)

    async def async_login_handler(self, account, regenerate_token=False):
        try:
            connector = ProxyConnector.from_url(rotate_proxy(True))
            async with aiohttp.ClientSession(
                connector=connector, conn_timeout=30
            ) as session:
                auth = Authenticator(
                    window=self.window,
                    open_id_config=self.open_id_config,
                    config=self.config,
                    session=session,
                )
                token = await auth.login_and_get_token(account[0], account[1])
                if not (auth.login_permission):
                    if account in self.accounts:
                        self.accounts.remove(account)
                    return
                if regenerate_token:
                    self.token = token
                    return
                if account[0] not in self.logged_users:
                    self.logged_users[account[0]] = []
                    self.logged_users[account[0]].append(account[1])
                self.logged_users[account[0]].append(token)
        except Exception as e:
            self.window.print_in_log(
                f"تعذر تسجيل الدخول للحساب {account[0]}", color=danger
            )
            print(f"LOGGING IN ERROR FOR - {account[0]}: ", e)
            if "argument" in str(e):
                return
            return await self.async_login_handler(account)

    async def login_handler(self):
        tasks = []
        for account in self.accounts:
            for _ in range(4):
                if account in self.accounts:
                    tasks.append(asyncio.create_task(self.async_login_handler(account)))
                else:
                    break

        await asyncio.gather(*tasks)

    async def async_run_tasks(self):
        tasks = []
        try:
            await self.login_handler()
            for user in self.logged_users:
                for token in self.logged_users[user][1:]:
                    tasks.append(
                        asyncio.create_task(
                            self.async_check_for_availabilty(user, token)
                        )
                    )
            if self.countdown:
                countdown = Countdown(self.target_h, self.target_min, self.target_sec)
                self.window.print_in_log(
                    f"في انتظار الساعة {countdown} للاستعلام عن المواعيد ...",
                    color=warning,
                )
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        except Exception as e:
            print("TASKS ERROR: ", e)

    def start_booking(self):
        try:
            if not (self.mode):
                self.accounts = [self.accounts[0]]
            asyncio.run(self.async_run_tasks())
            if self.token:
                self.window.add_accepted_account(self.username)
                self.availability = True
                asyncio.run(self.async_after_confirmation())
            if self.main_thread_flag == 0 or secretvars.MAIN_FLAG == 0:
                self.window.print_in_log("تم ايقاف البرنامج بنجاح", color=success)
            else:
                self.window.print_in_log(
                    "تم انهاء البرنامج بنجاح لانتهاء جميع الحسابات من الوظيفة",
                    color=success,
                )
        except Exception as e:
            print("Main Thread Error", e)
            self.window.print_in_log(
                f"حدث خطأ في البرنامج جاري اعادة المحاولة", color=danger
            )
            self.start_booking()
