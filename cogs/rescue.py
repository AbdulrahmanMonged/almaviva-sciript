import json
from .colors import *
from customtkinter import CTkInputDialog
from .Authenticator import Authenticator
from .sheet_management import *
from .utility import rotate_proxy
import aiohttp
from aiohttp_socks import ProxyConnector
from .required_info import *
import jwt


def wait_for_otp(token):
    decoded = jwt.decode(token, options={"verify_signature": False})
    phone_num = decoded["phone_number"]
    username = decoded["email"]
    xdxdxdxd = CTkInputDialog(
        text="Phone Num: {0}\nFor Account: {1}\nPress Okay to send OTP".format(
            phone_num, username
        ),
        title="OTP",
    )
    send_otp = xdxdxdxd.get_input()
    return send_otp


async def async_login_handler(account, window):
    try:
        connector = ProxyConnector.from_url(rotate_proxy(True))
        async with aiohttp.ClientSession(
            connector=connector, conn_timeout=30
        ) as session:
            auth = Authenticator(
                window=window,
                open_id_config=OPEN_ID_CONFIG,
                config=CONFIG,
                session=session,
            )
            token = await auth.login_and_get_token(account[0], account[1])
            if not (auth.login_permission):
                return
            return token
    except Exception as e:
        window.print_in_log(f"تعذر تسجيل الدخول للحساب {account[0]}", color=danger)
        print(f"LOGGING IN ERROR FOR - {account[0]}: ", e)
        if "argument" in str(e) and not (
            "Proxy" in str(e) or "Connection" in str(e) or "Error" in str(e)
        ):
            return
        return await async_login_handler(account, window)


def get_otp(window, token):
    phone_num = jwt.decode(token, options={"verify_signature": False})["phone_number"]
    window.print_in_log("جاري الحصول على الكود... OTP".format(phone_num), color=warning)
    otp = CTkInputDialog(text="Enter OTP", title="OTP")
    new_otp = otp.get_input()
    return new_otp


async def verify_otp(session, token, otp, window):
    try:
        if otp:
            window.print_in_log(("جاري التحقق من الكود... OTP"), color=warning)
            api_url = (
                f"https://egyapi.almaviva-visa.it/reservation-manager//api/otp/v1/{otp}"
            )
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
            result = await response.json()
            print(
                f"{datetime.now().strftime('%H:%M:%S:%f')} - Result of OTP Verification: {result}"
            )
            if response.status == 200 and result:
                window.print_in_log("تم التحقق من الكود... OTP", color=success)
                window.sign_otp(otp)
            if not (result):
                window.print_in_log("يوجد خطأ في التحقق من الكود... OTP", color=danger)
                otp = get_otp(window, token)
                if otp != None:
                    await verify_otp(session, token, otp, window)
            else:
                return

    except Exception as e:
        print("OTP VERIFICATION ERROR: ", e)
        window.print_in_log("يوجد خطأ في التحقق من الكود... OTP", color=info)


async def resend_otp(window, token):
    if not (wait_for_otp(token) == None):
        async with aiohttp.ClientSession(
            connector=ProxyConnector.from_url(rotate_proxy(True))
        ) as session:
            try:
                window.print_in_log("جاري ارسال الكود... OTP", color=warning)
                api_url = (
                    "https://egyapi.almaviva-visa.it/reservation-manager//api/otp/v1"
                )
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
                )
                if response.status == 200:
                    window.print_in_log("تم ارسال الكود... OTP", color=success)
                    result = await response.json()
                    print(
                        f"{datetime.now().strftime('%H:%M:%S:%f')} - Result of OTP sent: {result}"
                    )
                    if result.get("success"):
                        otp = get_otp(window, token)
                        if otp:
                            await verify_otp(session, token, otp, window)
                        else:
                            return
                    else:
                        return
                else:
                    return
            except Exception as e:
                print("OTP ERROR: ", e)
                window.print_in_log("يوجد خطأ في الارسال الكود... OTP", color=danger)


async def rescute_otp(account, window):
    window.print_in_log("تم بدأ برنامج اعادة ارسال . . . OTP", color=success)
    if account:
        token = await async_login_handler(account, window)
        if token:
            await resend_otp(window, token)
    else:
        window.print_in_log("لا يوجد حسابات متاحة", color=danger)
    window.resend_otp_btn.configure(state="enabled")
    window.print_in_log("تم انتهاء برنامج اعادة ارسال . . . OTP", color=success)
