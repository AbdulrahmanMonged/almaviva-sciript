import threading
import capsolver
import json
from .Document import Document
from .colors import *
from .Authenticator import Authenticator
from .sheet_management import *
import webbrowser
from .utility import rotate_proxy
from . import secretvars
from .Countdown import Countdown
import aiohttp
from aiohttp_socks import ProxyConnector
import asyncio
from .required_info import *
import jwt
import random
from .Applicant import Applicant
from uuid import uuid4
import asyncio
from anticaptchaofficial.recaptchav2proxyless import *


capsolver.api_key = "CAP-A2A8BE978B88F3AEED698FE58D47712A"


class Account:
    def __init__(self, data, window, office_id, serviceLevel, timing, countdown):
        self.window = window
        self.office_id = office_id
        self.serviceLevel = serviceLevel
        self.target_h, self.target_min, self.target_sec = timing
        self.username = data["username"]
        self.password = data["password"]
        self.documents = data["documents"]
        self.remaining_data = {
            "gender": data["gender"],
            "residenceAddress": data["residence_address"],
            "passportDateOfIssue": data["passport_issue_date"],
            "passportDateOfExpiry": data["passport_expiry_date"],
            "visa_id": data["visa_id"],
        }
        self.visa_id = self.remaining_data["visa_id"]
        self.token = ""
        self.checking_FLAG = 0
        self.config = CONFIG
        self.open_id_config = OPEN_ID_CONFIG
        self.main_thread_flag = 1
        self.countdown = countdown
        self.FLAG = 1
        self.availability = False
        self.recaptcha = ""
        self.payment_link = ""
        self.applicant = Applicant(**self.remaining_data)
        self.copied_documents = self.documents
        self.booked = False
        self.slots = []
        self.key = uuid4()
        self.solver = recaptchaV2Proxyless()
        self.solver.set_verbose(0)
        self.solver.set_key("8a77a79c369925e7886472762e2a21a8")
        self.solver.set_website_url("https://egy.almaviva-visa.it/appointment")
        self.solver.set_website_key("6Lf7DcMpAAAAAAg_D3VsyIZ_pUCGUH-vnWHkJH7M")
        self.solver.set_is_invisible(True)
        self.solver.set_soft_id(0)
        secretvars.accounts.append(self)
        self.captcha_count = 0

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

    async def main_program(self):

        await self.async_login_handler([self.username, self.password])
        if self.main_thread_flag:
            secretvars.ready_checking[str(self.key)] = True
            await self.async_check_for_availabilty()
            if self.availability:
                self.window.add_accepted_account(self.username)
                await self.async_after_confirmation()

    def continue_booking(self):
        asyncio.run(self.async_login_handler([self.username, self.password]))
        if self.main_thread_flag:
            self.availability = 1
            asyncio.run(self.async_after_confirmation())

    def search_fun(self):
        asyncio.run(self.main_program())

    async def async_login_handler(self, account):
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
                token = await auth.login_and_get_token(self.username, self.password)
                if not (auth.login_permission):
                    self.main_thread_flag = 0
                    return
                self.token = token
        except Exception as e:
            self.window.print_in_log(
                f"تعذر تسجيل الدخول للحساب {account[0]}", color=danger
            )
            print(f"LOGGING IN ERROR FOR - {account[0]}: ", e)
            if "argument" in str(e) and not (
                "Proxy" in str(e) or "Connection" in str(e) or "Error" in str(e)
            ):
                return
            return await self.async_login_handler([self.username, self.password])

    async def async_check_for_availabilty(self):
        checking_FLAG = 1
        api_url = f"https://egyapi.almaviva-visa.it/reservation-manager/api/planning/v1/checks?officeId={self.office_id}&visaId={self.visa_id}&serviceLevelId={self.serviceLevel}"
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
                            f"{datetime.now().strftime('%H:%M:%S:%f')} - Result of checking is '{(await response.text()).upper()}' Status code: '{response.status}' for user '{self.username}'"
                        )
                        if response.status == 200:
                            if await response.text() == "true":
                                self.window.print_in_log(
                                    f"تم الحصول علي مواعيد للمستخدم ... {self.username}",
                                    color=success,
                                )
                                self.availability = True
                                checking_FLAG = 0
                                return
                        if response.status == 429:
                            self.window.print_in_log(
                                f"لا يوجد مواعيد للمستخدم حاليا... {self.username}",
                                color=danger,
                            )
                            checking_FLAG = 0
                        if int(response.status) in range(401, 500):
                            checking_FLAG = 0

        except Exception as e:
            print("Cheking for availabilty ERROR: ", e)
            await self.async_check_for_availabilty()

    async def get_recaptcha(self):
        try:
            self.window.print_in_log("جاري التحقق من كابتشا...", color=warning)
            if self.captcha_count <= 10:
                response = capsolver.solve(
                    {
                        "type": "HCaptchaTaskProxyLess",
                        "websiteURL": "https://egy.almaviva-visa.it/appointment",
                        "websiteKey": "c4c0a5b8-7934-4172-9306-d67c5788aaa8",
                    }
                )
                self.recaptcha = response["gRecaptchaResponse"]
            # else:
            #     self.recaptcha = self.solver.solve_and_return_solution()
            self.captcha_count += 1
            self.window.print_in_log("تم التحقق من الكابتشا بنجاح", color=success)
        except Exception as e:
            print("captcha_error: ", e)
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
                    key=self.key,
                )
            )
        ).start()

    async def async_get_available_slots(self, session):
        try:
            self.window.print_in_log("جاري الحصول علي اماكن للحجز", color=warning)
            api_url = f"https://egyapi.almaviva-visa.it/reservation-manager/api/slots/v1/free?officeId={self.office_id}&quantity=1&date=2024-10-30&type=WEB"
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
            "passportNumber": decoded_token["passportNumber"],
            "dateOfBirth": decoded_token["dateOfBirth"],
        }
        self.name = decoded_token["name"]
        self.applicant.set_new_data(data)

    async def async_book(self, slots, session):
        try:
            if self.main_thread_flag and secretvars.MAIN_FLAG:
                data_gui = {}
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
                    "tripDate": "2024-10-30",
                    "tripDestination": "roma",
                    "termandcond": True,
                    "idServiceLevel": self.serviceLevel,
                    "applicants": [self.applicant.get_applicant_json()],
                    "slotStartDate": slot,
                    "source": "WEB",
                    "privacyPolicy": True,
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
                    data_gui["vidocall_url"] = (
                        f"https://egy.almaviva-visa.it/appointment/videocall?id={data["visaApplicationId"]}"
                    )
                    data_gui["applicant name"] = (
                        self.applicant.get_applicant_json()["name"]
                        + " "
                        + self.applicant.get_applicant_json()["surname"]
                    )
                    data_gui["Account_Email"] = self.username
                    threading.Thread(
                        target=lambda: asyncio.run(
                            db.set_video_call(data_gui["vidocall_url"], key=self.key)
                        )
                    ).start()
                    self.window.BookDataViewTopLevel(data_gui)

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
                        await db.check_passport(self.key)
                        self.get_another_passport()
                        return await self.async_book(slots, session)
                    if "IP" in result["message"]:
                        await session.close()
                        connector = ProxyConnector.from_url(rotate_proxy(True))
                        async with aiohttp.ClientSession(
                            connector=connector
                        ) as new_session:

                            return await self.async_book(slots, new_session)

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
                                db.write_user(self.username, self.password, self.key)
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
                        await self.async_login_handler([self.username, self.password])
                        self.applicant.set_bot(self)
                        if self.main_thread_flag and secretvars.MAIN_FLAG:
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
