import threading
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
import aiohttp
from aiohttp_socks import ProxyConnector
import asyncio
from awesometkinter.bidirender import render_text
from .required_info import *
import jwt
import random
from anticaptchaofficial.recaptchav2proxyless import *

capsolver.api_key = "CAP-CE0B6DD560FFC963B44E13E534D7782F"


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
        self.target_h = 7
        self.target_min = 59
        self.target_sec = 52
        self.copied_documents = self.documents
        self.logged_users = {}
        self.config = CONFIG
        self.open_id_config = OPEN_ID_CONFIG
        self.send_otp = None
        self.otp_verified = False
        self.name = ""
        self.solver = recaptchaV2Proxyless()
        self.solver.set_verbose(0)
        self.solver.set_key("8a77a79c369925e7886472762e2a21a8")
        self.solver.set_website_url("https://egy.almaviva-visa.it/appointment")
        self.solver.set_website_key("6Lc4mLUpAAAAAN0TB4rHNAQS1Zbt5yfghaZ17w-A")
        self.solver.set_is_invisible(True)
        self.solver.set_soft_id(0)

    def add_applicant(self, applicant):
        applicant.set_bot(self)
        self.applicant = applicant

    def wait_for_otp(self):
        xdxdxdxd = CTkInputDialog(
            text="Phone Num: {0}\nFor Account: {1}\nPress Okay to send OTP".format(
                self.applicant.get_phone_number(), self.username
            ),
            title="OTP",
        )
        self.send_otp = xdxdxdxd.get_input()
        return self.send_otp

    def get_otp(self):
        self.otp = ""
        self.window.print_in_log(
            "جاري الحصول على الكود... OTP".format(self.applicant.get_phone_number()),
            color=warning,
        )
        otp = CTkInputDialog(text="Enter OTP", title="OTP")
        self.otp = otp.get_input()

    def get_another_passport(self):

        self.window.print_in_log(
            "الباسبورت مربوط بمستخدم اخر برجاء اضافة باسبورت جديد", color=danger
        )
        new_passport = list(self.applicant.get_passport_number())
        new_passport.insert(
            random.randint(0, len(self.applicant.get_passport_number()) - 1), "\u200b"
        )
        new_str = "".join(new_passport)
        self.applicant.set_passport_number(new_str)

    async def verify_otp(self, session):

        try:
            if self.otp:
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
                result = await response.json()
                print(
                    f"{datetime.now().strftime('%H:%M:%S:%f')} - Result of OTP Verification: {result}"
                )
                if response.status == 200 and result:
                    self.window.print_in_log("تم التحقق من الكود... OTP", color=success)
                    self.window.sign_otp(self.otp)
                    self.otp_verified = True
                if not (result) and self.main_thread_flag:
                    self.window.print_in_log(
                        "يوجد خطأ في التحقق من الكود... OTP", color=danger
                    )
                    self.get_otp()
                    await self.verify_otp(session)
            else:
                self.main_thread_flag = 0

        except Exception as e:
            print("OTP VERIFICATION ERROR: ", e)
            self.window.print_in_log("يوجد خطأ في التحقق من الكود... OTP", color=info)

    async def get_recaptcha(self):
        try:
            self.window.print_in_log("جاري التحقق من كابتشا...", color=warning)
            self.recaptcha = self.solver.solve_and_return_solution()
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
                    f"https://eu.gateway.mastercard.com/checkout/pay/{payment_link}?checkoutVersion=1.0.0",
                )
            )
        ).start()

    async def async_get_available_slots(self, session):
        try:
            self.window.print_in_log("جاري الحصول علي اماكن للحجز", color=warning)
            api_url = f"https://egyapi.almaviva-visa.it/reservation-manager/api/slots/v1/free?officeId={self.office_id}&quantity=1&date=2024-09-30&type=WEB"
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
            result = await response.json()
            print(
                f"{datetime.now().strftime('%H:%M:%S:%f')} - Result of AVAILABLE SLOTS: {result}"
            )
            try:
                if not ("Internal Error" in result.get("message")):
                    self.window.print_in_log("تم الحصول علي اماكن للحجز", color=success)
            finally:
                return result
        except Exception as e:
            print("SLOTS ERROR ", e)
            self.window.print_in_log("يوجد خطأ في الحصول علي اماكن للحجز", color=danger)

    async def async_send_otp(self, session):
        try:
            if not (self.wait_for_otp() == None):
                self.window.print_in_log("جاري ارسال الكود... OTP", color=warning)
                api_url = (
                    "https://egyapi.almaviva-visa.it/reservation-manager//api/otp/v1"
                )
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
                    if result.get("success"):
                        self.get_otp()
                        if self.otp:
                            await self.verify_otp(session)
                        else:
                            self.main_thread_flag = 0
                    else:
                        self.main_thread_flag = 0
            else:
                self.main_thread_flag = 0
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

    async def async_get_account_data(self):
        decoded_token = jwt.decode(self.token, options={"verify_signature": False})
        data = {
            "name": decoded_token["given_name"],
            "family_name": decoded_token["family_name"],
            "email": decoded_token["email"],
            "phone": decoded_token["phone_number"],
        }
        self.name = decoded_token["name"]
        self.applicant.set_new_data(data)

    async def async_book(self, slots, session):
        try:
            if self.main_thread_flag:
                slot = random.choice(slots)
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Recaptcha": self.recaptcha,
                    "Accept-Language": "en",
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/plain, */*",
                    "DeviceOperatingSystem": "web",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "Origin": "https://egy.almaviva-visa.it",
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": "Windows",
                }
                body = {
                    "officeId": self.office_id,
                    "tripDate": "2024-09-30",
                    "tripDestination": "roma",
                    "termandcond": True,
                    "idServiceLevel": self.serviceLevel,
                    "applicants": [self.applicant.get_applicant_json()],
                    "slotStartDate": slot,
                    "source": "WEB",
                    "privacyPolicy": True,
                    "otp": self.otp,
                }
                URL = "https://egyapi.almaviva-visa.it/reservation-manager/api/visa-applications/v1/checkout?paymentProvider=MASTERCARD"
                response = await session.post(
                    URL, headers=headers, data=json.dumps(body)
                )
                self.window.print_in_log("جاري الحجز...", color=warning)
                print(response.status, await response.text())
                result = await response.json()
                if response.status == 201:
                    self.booked = 1
                    self.window.print_in_log("تم الحجز بنجاح", color=success)
                    data = await response.json()
                    self.payment_link = data["sessionId"]
                    self.main_thread_flag = 0
                    secretvars.data["booked"] = True
                    threading.Thread(
                        target=lambda: asyncio.run(
                            db.update_account(self.window, self.name)
                        )
                    ).start()
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
                        return await self.async_book(slots, session)
                    if "captcha" in result["message"].lower():
                        self.window.print_in_log(
                            "تم انتهاء الكابتشا...جاري حل الكابشتا من جديد",
                            color=danger,
                        )
                        await self.get_recaptcha()
                        return await self.async_book(slots, session)
                    if "Passport" in result["message"]:
                        await db.check_passport()
                        self.get_another_passport()
                        return await self.async_book(slots, session)
        except Exception as e:
            print("BOOKING ERROR", e)
            return await self.async_book(slots, session)

    async def async_after_confirmation(self):
        try:
            connector = ProxyConnector.from_url(rotate_proxy(True))
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [
                    self.async_get_available_slots(session),
                    self.async_upload_documents(session),
                    self.async_get_account_data(),
                ]
                if self.availability and (not self.booked):
                    responses = await asyncio.gather(*tasks)
                    slots = responses[0]
                    if type(slots) == dict:
                        if "Internal Error" in slots.get("message"):
                            self.window.print_in_log(
                                "عذرا لا يوحد مواعيد للحجز تم الغاء المهمة",
                                color=danger,
                            )
                            return
                    elif type(slots) == list:
                        threading.Thread(
                            target=lambda: asyncio.run(
                                db.write_user(self.username, self.password)
                            )
                        ).start()
                        secretvars.data["accepted"] = True
                        secretvars.data["users"] = []
                        secretvars.data["users"].append(
                            {
                                "name": self.username,
                                "password": self.password,
                                "accepted": True,
                            }
                        )
                        threading.Thread(
                            target=lambda: asyncio.run(
                                db.update_account(self.window, self.name)
                            )
                        ).start()
                        await self.async_login_handler(
                            [self.username, self.password], True
                        )
                        if not self.otp and self.main_thread_flag:
                            await self.async_send_otp(session)
                        else:
                            self.otp_verified = 1

                        self.applicant.set_bot(self)
                        new_passport = list(self.applicant.get_passport_number())
                        new_passport.insert(
                            random.randint(
                                0, len(self.applicant.get_passport_number()) - 1
                            ),
                            "\u200b",
                        )
                        new_str = "".join(new_passport)
                        self.applicant.set_passport_number(new_str)
                        if self.main_thread_flag and self.otp_verified:
                            await self.get_recaptcha(),
                            await self.async_book(slots=slots, session=session)
                            if self.payment_link:
                                self.write_payment_link(self.payment_link)
                            if self.main_thread_flag == 0 or secretvars.MAIN_FLAG == 0:
                                return
                    else:
                        self.window.print_in_log(
                            "عذرا لا يوجد مواعيد متاحة للحجز...برجاء المحاولة مرة اخري",
                            color=danger,
                        )
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
                if self.main_thread_flag:
                    print(
                        f"TARGET TIME REACHED - {datetime.now().strftime('%H:%M:%S:%f')}"
                    )
                    while (
                        self.FLAG
                        and self.main_thread_flag
                        and secretvars.MAIN_FLAG
                        and checking_FLAG
                    ):
                        tasks = [
                            session.get(api_url, headers=headers) for _ in range(1)
                        ]
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
                        if response.status == 429:
                            self.window.print_in_log(
                                f"لا يوجد مواعيد للمستخدم حاليا... {user}", color=danger
                            )
                            checking_FLAG = 0
                        if int(response.status) in range(400, 500):
                            checking_FLAG = 0
                    await asyncio.sleep(300)

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
            if regenerate_token:
                return await self.async_login_handler(account, regenerate_token=True)
            self.window.print_in_log(
                f"تعذر تسجيل الدخول للحساب {account[0]}", color=danger
            )
            print(f"LOGGING IN ERROR FOR - {account[0]}: ", e)
            if "argument" in str(e) and not (
                "Proxy" in str(e) or "Connection" in str(e) or "Error" in str(e)
            ):
                return
            return await self.async_login_handler(account)

    async def login_handler(self):
        tasks = []
        for account in self.accounts:
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
                self.username = self.accounts[0][0]
                self.password = self.accounts[0][1]
                asyncio.run(self.login_handler())
                self.token = self.logged_users[self.username][1]
            else:
                asyncio.run(self.async_run_tasks())

            if self.token:
                if self.mode:
                    self.window.add_accepted_account(self.username)
                self.window.resend_otp_btn.configure(state="enabled")
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
