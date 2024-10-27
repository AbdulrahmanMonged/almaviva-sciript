import threading
import capsolver
from .colors import *
from .sheet_management import *
from . import secretvars
from .Countdown import Countdown
import asyncio
from .required_info import *
from .Account import Account
capsolver.api_key = "CAP-A2A8BE978B88F3AEED698FE58D47712A"


class Bot:
    def __init__(
        self,
        window,
        applicant,
        documents,
        office_id=1,
        visa_id=3,
        serviceLevel=1,
        countdown=0,
        otp="",
        saved_customers=True,
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
        self.availability = False
        self.serviceLevel = serviceLevel
        self.countdown = countdown
        self.FLAG = 1
        self.booked = 0
        self.target_h = 7
        self.target_min = 59
        self.target_sec = 57
        self.copied_documents = self.documents
        self.logged_users = {}
        self.config = CONFIG
        self.open_id_config = OPEN_ID_CONFIG
        self.send_otp = None
        self.otp_verified = False
        self.name = ""
        self.saved_customers = saved_customers
        self.checking_flag = True
  

            
    async def testing_function(self):

        tasks = []
        for account in self.accounts:
            account_obj = Account(account,
                                self.window,
                                self.office_id, 
                                self.serviceLevel,
                                [self.target_h, self.target_min, self.target_sec],
                                self.countdown,
                )
            tasks.append(asyncio.create_task(account_obj.main_program()))
            secretvars.ready_checking[str(account_obj.key)] = False
        threading.Thread(target=lambda: asyncio.run(self.check_for_accounts())).start()
        await asyncio.gather(*tasks)
        
    async def check_for_accounts(self):
        try:
            while secretvars.MAIN_FLAG and self.checking_flag:
                check_flag = True
                values = secretvars.ready_checking.values()
                for check  in values:
                    if not check:
                        await asyncio.sleep(1)
                        check_flag = False
                if check_flag:
                    self.checking_flag = False
            if self.countdown:
                countdown = Countdown(self.target_h, self.target_min, self.target_sec)
                self.window.print_in_log(
                            f"في انتظار الساعة {countdown} للاستعلام عن المواعيد ...",
                            color=warning,
                        )
        except Exception as e:
            await self.check_for_accounts()
        
        
    def start_booking(self):
        try:
            secretvars.ready_checking = {}
            asyncio.run(self.testing_function())
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
