from customtkinter import *
from awesometkinter.bidirender import render_text
from .Applicant import Applicant
from tkinter import messagebox
import os
from datetime import datetime
from .colors import *
from .almaviva_script import Bot
from threading import Thread
import webbrowser
from .Countdown import Countdown
from . import secretvars
from .sheet_management import db
import asyncio
from pprint import pp
from .Account import Account


class App2(CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.target_hour = 7
        self.target_minute = 59
        self.target_second = 57
        self.count = 0
        self.labels = []
        self.applicant = None
        self.applicants = []
        self.new_users = []

        self.bot = None
        self.start_delay = None
        self.saved_operations = False
        self.visa_id = 3
        self.documents = (
            {"passport": [None, 100]}
            if self.visa_id != 3
            else {
                "nulla": [None, 187],
                "passport": [None, 100],
                "phoneNumber": [None, 188],
            }
        )
        self.toplevel_window = None
        self.accounts_window = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.navigation_frame = CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(7, weight=1)

        self.navigation_frame_label = CTkLabel(
            self.navigation_frame,
            text="  ALMAVIVA",
            compound="left",
            font=CTkFont(size=15, weight="bold"),
        )
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text=render_text("تسجيل الدخول "),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.home_button_event,
        )
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_4_button = CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text=render_text("الحسابات"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.frame_4_button_event,
        )
        self.frame_4_button.grid(row=2, column=0, sticky="ew")

        self.frame_5_button = CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text=render_text("التقارير"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.frame_5_button_event,
        )
        self.frame_5_button.grid(row=6, column=0, sticky="ew")

        self.home_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.third_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.fourth_frame = CTkScrollableFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.fifth_frame = CTkScrollableFrame(
            self, corner_radius=0, fg_color="transparent"
        )

        if self.saved_operations:
            self.enable_saved_customers()

        self.select_frame_by_name("home")

        for frame in [self.home_frame, self.second_frame, self.third_frame]:
            frame.grid_columnconfigure(0, weight=4, minsize=5)
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_columnconfigure(2, weight=4)

        self.fifth_frame.grid_columnconfigure(0, weight=5)
        self.fourth_frame.grid_columnconfigure(0, weight=5)

        self.fill_data_toplevel_window = None
        self.book_data_toplevel_window = None
        self.top_views = []

        
        ###############################  HOME_FRAME #####################################

        self.username_label = CTkLabel(
            self.home_frame, text=render_text("اسم المستخدم")
        )
        self.add_applicant_btn = CTkButton(
            self.home_frame,
            width=170,
            text=render_text("اضافة مستخدم"),
            command=self.open_fillDataTopLevel,
        )
        self.add_applicant_btn.grid(row=2, column=1, sticky="s", padx=5, pady=5)
        self.save_password_check = StringVar(value="on")
        self.start_with_timer_check = StringVar(value="on")

        self.start_with_timer_lbl = CTkLabel(
            self.home_frame, text=render_text("بدء الساعة التاسعة صباحا")
        )

        self.office_id_lbl = CTkLabel(self.home_frame, text=render_text("المكتب"))
        self.office_id_lbl.grid(row=4, column=2, sticky="s", padx=5, pady=5)
        self.office_id_option = CTkOptionMenu(
            self.home_frame, values=["Cairo", "Alexandria"], width=170
        )
        self.office_id_option.grid(row=4, column=1, sticky="s", padx=5, pady=5)

        self.visa_price_lbl = CTkLabel(self.home_frame, text=render_text("سعر الفيزا"))
        self.visa_price_lbl.grid(row=5, column=2, sticky="s", padx=5, pady=5)
        self.visa_price_options = CTkOptionMenu(
            self.home_frame, values=["Standard - EGP 1750", "Vip - EGP 3810"], width=170
        )
        self.visa_price_options.grid(row=5, column=1, sticky="s", padx=5, pady=5)

        self.start_with_timer_lbl.grid(row=9, column=2, sticky="s", padx=5, pady=5)
        self.start_with_timer_switch = CTkSwitch(
            self.home_frame,
            text="",
            variable=self.start_with_timer_check,
            onvalue="on",
            offvalue="off",
        )
        self.start_with_timer_switch.grid(row=9, column=1, sticky="s", padx=5, pady=5)

        self.start_program_button = CTkButton(
            self.home_frame,
            text=render_text("بدا البرنامج"),
            command=self.start_execution,
        )
        self.start_program_button.grid(row=10, column=2, sticky="s", padx=5, pady=5)
        self.home_disable_btn = CTkButton(
            self.home_frame,
            text=render_text("تعطيل البرنامج"),
            command=self.stop_execution,
            state="disabled",
        )
        self.home_disable_btn.grid(row=10, column=0, sticky="s", padx=5, pady=5)

        #############################ACCOUNTS FRAME######################################
        self.account_test = AccountFrame(
            {"username": "Email/Username", "password": "Password"},
            True,
            self.fourth_frame,
        )
        self.account_test.grid(
            row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5
        )

        #############################################################################

        self.home_frame.grid_rowconfigure(10, weight=1)
        self.second_frame.grid_rowconfigure(10, weight=1)
        self.third_frame.grid_rowconfigure(4, weight=1)

        #############################################################################

        for frame in (self.home_frame, self.second_frame):
            for child in frame.winfo_children():
                if isinstance(child, CTkEntry):
                    child.bind("<Button-3>", self.right_click_event)

    def select_frame_by_name(self, name):
        self.home_button.configure(
            fg_color=("gray75", "gray25") if name == "home" else "transparent"
        )
        self.frame_5_button.configure(
            fg_color=("gray75", "gray25") if name == "frame_5" else "transparent"
        )
        self.frame_4_button.configure(
            fg_color=("gray75", "gray25") if name == "frame_4" else "transparent"
        )
        if self.saved_operations:
            self.frame_6_button.configure(
                fg_color=("gray75", "gray25") if name == "frame_6" else "transparent"
            )
            if name == "frame_6":
                self.sixth_frame.grid(row=0, column=1, sticky="nsew")
            else:
                self.sixth_frame.grid_forget()

        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()

        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()

        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

        if name == "frame_5":
            self.fifth_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.fifth_frame.grid_forget()

        if name == "frame_4":
            self.fourth_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.fourth_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def frame_5_button_event(self):
        self.select_frame_by_name("frame_5")

    def frame_6_button_event(self):
        self.customers_display.customers = []
        Thread(target=lambda: asyncio.run(db.get_accounts(self))).start()

        self.select_frame_by_name("frame_6")

    def frame_4_button_event(self):
        self.select_frame_by_name("frame_4")

    def add_applicant(self, data, validate=True):
        account_test = AccountFrame(data, False, self.fourth_frame)
        account_test.grid(
            row=len(self.applicants) + 1,
            column=0,
            columnspan=3,
            sticky="nsew",
            padx=5,
            pady=5,
        )
        self.applicants.append(account_test)
        self.print_in_log(f"تم حفظ {data["username"]} بنجاح", color=info)

    def validation(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, CTkEntry):
                if child.get() == "":
                    return False
        return True

    def browse_file(self, type, file_path=None, should_pop_up=True):
        if should_pop_up:
            file_path = filedialog.askopenfilename(
                initialdir=os.curdir, title="Select a File"
            )
        if not (os.path.exists(file_path)):
            messagebox.showerror(
                title="خطأ",
                message="الملف {0} غير موجود".format(file_path.split("/")[-1]),
            )
            return
        self.documents[type][0] = file_path
        match type:
            case "passport":
                self.print_in_log("تم تحديد جواز السفر", color=info)
                self.passport_img_state.configure(
                    text=file_path.split("/")[-1], text_color=success
                )
                secretvars.data["media"]["passport"] = file_path
            case "nulla":
                self.print_in_log("تم تحديد صورة الهوية", color=info)
                self.nulla_img_state.configure(
                    text=file_path.split("/")[-1], text_color=success
                )
                secretvars.data["media"]["nulla"] = file_path
            case "phoneNumber":
                self.print_in_log("تم تحديد رقم الهاتف", color=info)
                self.phonenum_img_state.configure(
                    text=file_path.split("/")[-1], text_color=success
                )
                secretvars.data["media"]["phoneNumber"] = file_path

    def print_in_log(self, text, color=info, url=""):
        current_time = datetime.now().strftime("%H:%M:%S")
        label = CTkLabel(
            self.fifth_frame,
            text=render_text(f"[{current_time}] - {text}"),
            text_color=color,
            font=CTkFont(size=14, weight="bold"),
        )

        if self.count > 500:
            self.labels[0].destroy()
            self.labels.remove(self.labels[0])
        label.grid(row=self.count, column=0, sticky="e", padx=0, pady=0)
        self.count += 1
        self.labels.append(label)
        if url:
            label.configure(cursor="hand2")
            label.bind("<Button-1>", lambda e: webbrowser.open(url))
        self.fifth_frame.after(10, self.fifth_frame._parent_canvas.yview_moveto, 1.0)

    def save_img_data(self):
        for key in self.documents:
            if not (self.documents[key][0]):
                messagebox.showerror(title="خطأ", message="برجاء تحديد جميع المستندات")
                self.select_frame_by_name("frame_3")
                return False
        for child in self.third_frame.winfo_children():
            if isinstance(child, CTkButton):
                child.configure(state="disabled")
        self.img_edit_button.configure(state="normal")
        self.print_in_log("تم حفظ المستندات", color=success)

    def edit_img_data(self):
        for child in self.third_frame.winfo_children():
            if isinstance(child, CTkButton):
                child.configure(state="normal")
        self.img_edit_button.configure(state="disabled")

    def disable_home_data(self):
        for child in self.home_frame.winfo_children():
            if (
                isinstance(child, CTkEntry)
                or isinstance(child, CTkButton)
                or isinstance(child, CTkSwitch)
                or isinstance(child, CTkCheckBox)
                or isinstance(child, CTkOptionMenu)
            ):
                try:
                    child.configure(state="disabled")
                except:
                    child.disable_component()
        self.home_disable_btn.configure(state="normal")

    def enbale_home_data(self):
        for child in self.home_frame.winfo_children():
            if (
                isinstance(child, CTkEntry)
                or isinstance(child, CTkButton)
                or isinstance(child, CTkSwitch)
                or isinstance(child, CTkCheckBox)
                or isinstance(child, CTkOptionMenu)
            ):
                try:
                    child.configure(state="normal")
                except:
                    child.enable_component()
        self.home_disable_btn.configure(state="disabled")

    def stop_execution(self):
        try:
            self.after_cancel(self.start_delay)
        finally:
            self.print_in_log("تم ايقاف البرنامج", color=warning)
            # self.enable_applcant_data()
            self.enbale_home_data()
            # self.edit_img_data()
            secretvars.MAIN_FLAG = 0
            self.bot.main_thread_flag = 0
            self.bot = None
            if secretvars.accounts:
                for account in secretvars.accounts:
                    account.main_thread_flag = 0
                secretvars.accounts = []

            self.enbale_home_data()

    def start_execution(self):
        if not self.validate_all_fields():
            return
        self.disable_home_data()
        countdown = Countdown(self.target_hour, 55, 0)
        future_countdown = Countdown(
            self.target_hour, self.target_minute, self.target_second
        )
        if self.start_with_timer_check.get() == "on":
            if not (
                countdown.get_remaining_time() > future_countdown.get_remaining_time()
            ):
                self.start_delay = self.after(
                    countdown.time_to_start_program(), self.bot_excution
                )
                self.print_in_log(f"البرنامج سيبدأ في {countdown}", color=warning)
            else:
                self.bot_excution()
        else:
            self.bot_excution()
        self.select_frame_by_name("frame_5")

    def bot_excution(self):
        secretvars.MAIN_FLAG = 1
        self.bot = Bot(
            self,
            self.applicant,
            self.documents,
            self.office_id_option.get(),
            self.visa_id,
            1 if self.visa_price_options.get() == "Standard - EGP 1750" else 2,
            self.start_with_timer_check.get() == "on",
            "",
            self.saved_operations,
        )
        self.bot.accounts = self.get_all_applicants()
        Thread(target=self.bot.start_booking).start()

    def right_click_event(self, event):
        clipboard_content = event.widget.clipboard_get()
        processed_content = clipboard_content.strip()
        event.widget.insert("insert", processed_content)
        return "break"

    def validate_all_fields(self):
        if len(self.applicants) == 0:
            messagebox.showerror(
                title="خطأ", message="برجاء تحديد مستخدم واحد علي الاقل"
            )
            self.select_frame_by_name("frame_4")
            return False
        return True

    def get_all_applicants(self):
        return [applicant.get_applicant_data() for applicant in self.applicants]

    def open_toplevel(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)
        else:
            self.toplevel_window.focus()

    def open_account_window(self):
        if self.accounts_window is None or not self.accounts_window.winfo_exists():
            self.accounts_window = AccountsManager(self)
        else:
            self.accounts_window.focus()

    def add_accepted_account(self, user):
        self.open_toplevel()
        self.toplevel_window.add_account(user)
        self.change_color_for_accepted_user(user)

    def change_color_for_accepted_user(self, user):
        for account in self.applicants:
            if account.get_applicant_data()["username"] == user:
                account.change_color()
                break

    def clear_all_entries(self):
        for widget in self.second_frame.winfo_children():
            if isinstance(widget, CTkEntry):
                widget.delete(0, "end")

        for widget in self.home_frame.winfo_children():
            if isinstance(widget, CTkEntry):
                widget.delete(0, "end")

    def load_data(self, data):
        try:
            for account in self.applicants:
                account.destroy()
            self.enable_applcant_data()
            self.edit_img_data()
            self.enbale_home_data()
            self.clear_all_entries()
            account_data = data["account_data"]
            users = data["users"]
            media = data["media"]
            self.gender_entry.set(
                render_text("ذكر")
                if account_data["gender"] == "M"
                else render_text("انثي")
            )
            self.residenceAddress_entry.insert(0, account_data["residenceAddress"])
            self.passportDateOfIssue_entry.insert(
                0, account_data["passportDateOfIssue"]
            )
            self.passportDateOfExpiry_entry.insert(
                0, account_data["passportDateOfExpiry"]
            )
            for user in users:
                self.add_applicant(user["name"], user["password"], False)
            for key in media:
                if media[key]:
                    self.browse_file(key, media[key], False)

            # self.otp_entry.insert(0, data["otp"])
            self.office_id_option.set(data["office"])
            self.visa_price_options.set(data["visa_price"])

        except Exception as e:
            print(e)
            self.enable_customer_display()

    def disable_customer_display(self):
        self.customer_manager.disable()
        self.customers_display.disable()

    def enable_customer_display(self):
        self.customer_manager.enable()
        self.customers_display.enable()

    def refresh_customer_display(self):
        self.frame_6_button_event()

    def enable_saved_customers(self):
        self.frame_6_button = CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text=render_text("العمليات المحفوظة"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.frame_6_button_event,
        )
        self.frame_6_button.grid(row=5, column=0, sticky="ew")
        self.sixth_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")

        ###############################SAVED OPERATIONS#####################################
        self.customers_display = CustomerDisplay(self.sixth_frame)
        self.customers_display.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.customer_manager = CustomersManagement(self.sixth_frame)
        self.customer_manager.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        #####################################################################################

        self.sixth_frame.grid_columnconfigure(0, weight=1)
        self.sixth_frame.grid_rowconfigure(0, weight=9)
        self.sixth_frame.grid_rowconfigure(1, weight=1)

    def open_fillDataTopLevel(self):
        if (
            self.fill_data_toplevel_window is None
            or not self.fill_data_toplevel_window.winfo_exists()
        ):
            self.fill_data_toplevel_window = FillData(self)
        else:
            self.fill_data_toplevel_window.focus()

    def BookDataViewTopLevel(self, data):
        book_data_view_toplevel = BookDataView(self, data)
        self.top_views.append(book_data_view_toplevel)

    def recieve_data_from_fillData(self, data):
        self.add_applicant(data)

    def update_account(self, data, account_obj):
        self.open_fillDataTopLevel()
        self.fill_data_toplevel_window.update_data(data, account_obj)

    def get_timing(self):
        return [self.target_hour, self.target_minute, self.target_second]


class AccountFrame(CTkFrame):
    def __init__(self, data, hidden=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

        self.name = StringVar(self, data["username"])
        self.password = StringVar(self, data["password"])
        self.name.set
        self.main_window = self.master.master.master.master
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="column")

        self.account_name = CTkLabel(
            self, textvariable=self.name, font=CTkFont(size=12)
        )
        self.account_password = CTkLabel(
            self, textvariable=self.password, font=CTkFont(size=12)
        )
        self.account_name.grid(row=0, column=5, sticky="nsew", padx=10)
        self.account_password.grid(row=0, column=4, sticky="nsew", padx=10)
        if not (hidden):
            self.delet_btn = CTkButton(
                self,
                text=render_text("حذف"),
                command=self.delete,
                font=CTkFont(size=12),
                fg_color=danger_btn,
                hover_color=danger_hover,
            )
            self.delet_btn.grid(row=0, column=3, sticky="nsew", padx=10)
            self.update_btn = CTkButton(
                self,
                text=render_text("تعديل"),
                font=CTkFont(size=12),
                fg_color=warning_btn,
                hover_color=warning_hover,
                command=self.update_account,
            )
            self.update_btn.grid(row=0, column=2, sticky="nsew", padx=10)
            self.continue_btn = CTkButton(
                self,
                text=render_text("استكمال حجز"),
                font=CTkFont(size=12),
                fg_color=primary_btn,
                hover_color=primary_hover,
                command=self.continue_booking,
            )
            self.continue_btn.grid(row=0, column=1, sticky="nsew", padx=10)

            self.search_for_availability_btn = CTkButton(
                self,
                text=render_text("البحث عن مواعيد"),
                font=CTkFont(size=12),
                fg_color=success_btn,
                hover_color=success_hover,
                command=self.search_for_availability_fun,
            )
            self.search_for_availability_btn.grid(
                row=0, column=0, sticky="nsew", padx=10
            )

    def delete(self):
        self.main_window.applicants.remove(self)
        self.destroy()

    def get_applicant_data(self):
        self.data["visa_id"] = self.main_window.visa_id
        return self.data

    def change_color(self):
        self.account_name.configure(text_color=success)
        self.account_password.configure(text_color=success)

    def update_account(self):
        self.main_window.update_account(self.data, self)

    def continue_booking(self):
        account = Account(
            self.get_applicant_data(),
            self.main_window,
            1 if self.main_window.office_id_option.get() == "Cairo" else 2,
            (
                1
                if self.main_window.visa_price_options.get() == "Standard - EGP 1750"
                else 2
            ),
            self.main_window.get_timing(),
            False,
        )
        secretvars.MAIN_FLAG = 1
        Thread(target=account.continue_booking).start()
        self.main_window.disable_home_data()
        self.main_window.select_frame_by_name("frame_5")

    def search_for_availability_fun(self):
        account = Account(
            self.get_applicant_data(),
            self.main_window,
            1 if self.main_window.office_id_option.get() == "Cairo" else 2,
            (
                1
                if self.main_window.visa_price_options.get() == "Standard - EGP 1750"
                else 2
            ),
            self.main_window.get_timing(),
            False,
        )
        secretvars.MAIN_FLAG = 1
        Thread(target=account.search_fun).start()
        self.main_window.disable_home_data()
        self.main_window.select_frame_by_name("frame_5")


class CustomersManagement(CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_window = self.master.master
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")
        self.customer_lbl = CTkLabel(
            self, text=render_text("اسم العميل"), font=CTkFont(size=15)
        )
        self.customer_entry = CTkEntry(self, width=100)
        self.save_customer_btn = CTkButton(
            self,
            text=render_text("حفظ"),
            font=CTkFont(size=15, weight="bold"),
            width=100,
            command=self.save_customer,
            fg_color=success_btn,
            hover_color=success_hover,
        )

        self.customer_lbl.grid(row=0, column=2, sticky="nsew", padx=5)
        self.customer_entry.grid(row=0, column=1, sticky="nsew", padx=5)
        self.save_customer_btn.grid(row=0, column=0, sticky="nsew", padx=5)

        self.customer_entry.bind("<KeyRelease>", self.on_entry_change)

        self.progress_bar = None
        self.progress_label = None

    def on_entry_change(self, event):
        text = self.customer_entry.get()
        self.main_window.customers_display.filter_customers(text)

    def save_customer(self):
        if self.customer_entry.get() == "":
            messagebox.showerror("خطأ", "برجاء عدم ترك خانة اسم العميل فارغة")
            return

        if not (self.main_window.validate_all_fields()):
            return

        name = self.customer_entry.get()
        secretvars.data["office"] = self.main_window.office_id_option.get()
        secretvars.data["visa_price"] = self.main_window.visa_price_options.get()
        # secretvars.data["otp"] = self.main_window.otp_entry.get()
        users = self.main_window.get_all_applicants()
        secretvars.data["users"] = []
        for user in users:
            secretvars.data["users"].append(
                {"name": user[0], "password": user[1], "accepted": False}
            )
        Thread(
            target=lambda: asyncio.run(db.save_account(self.main_window, name))
        ).start()
        self.customer_entry.delete(0, "end")

    def disable(self):
        self.customer_entry.configure(state="disabled")
        self.save_customer_btn.configure(state="disabled")

    def enable(self):
        self.customer_entry.configure(state="normal")
        self.save_customer_btn.configure(state="normal")


class CustomerDisplay(CTkScrollableFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customers = []
        self.grid_columnconfigure(0, weight=1)
        self.display_customers(self.customers)

    def filter_customers(self, text):
        new_customers = [
            customer for customer in self.customers if text in customer.name
        ]
        self.display_customers(new_customers)

    def forgeT_all_componoents(self):
        for customer in self.winfo_children():
            customer.grid_forget()

    def display_customers(self, customers):
        self.forgeT_all_componoents()
        accepted_customers = [
            customer
            for customer in customers
            if customer.is_accepted and not customer.is_booked
        ]
        booked_customers = [customer for customer in customers if customer.is_booked]
        rest_of_customers = [
            customer
            for customer in customers
            if not customer.is_accepted and not customer.is_booked
        ]
        total = accepted_customers + booked_customers + rest_of_customers
        for m in range(len(total)):
            total[m].grid(row=m, column=0, sticky="nsew", pady=5, padx=5)

    def add_customer(
        self, customer_name, owner_id, customer_id, is_accepted, is_booked
    ):
        customer = Customer(
            master=self,
            name=customer_name,
            id=customer_id,
            is_accepted=is_accepted,
            is_booked=is_booked,
            owner_id=owner_id,
        )
        self.customers.append(customer)

    def refresh(self):
        self.destroy_spinner()
        self.display_customers(self.customers)

    def disable(self):
        try:

            for child in self.customers:

                child.disable()
        except Exception as e:
            pass

    def enable(self):
        try:
            for child in self.customers:
                child.enable()
        except Exception as e:
            pass

    def show_spinner(self):
        self.progress_bar = CTkProgressBar(
            self, mode="indeterminate", indeterminate_speed=1, progress_color=warning
        )
        self.progress_label = CTkLabel(
            self,
            text="جاري التحميل",
            font=CTkFont(family="Segoe UI", size=15),
            text_color=warning,
        )
        self.progress_bar.start()
        self.progress_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.progress_bar.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def destroy_spinner(self):
        self.progress_bar.destroy()
        self.progress_label.destroy()


class Customer(CTkFrame):
    def __init__(self, name, id, owner_id, is_accepted, is_booked, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = self.master.master.master.master.master
        self.is_accepted = is_accepted
        self.is_booked = is_booked
        self.id = id
        self.name = name
        self.owner_id = owner_id

        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")

        self.customer_lbl = CTkLabel(
            self, text=self.name, font=CTkFont(size=12, weight="bold")
        )

        if self.is_booked:
            self.customer_lbl.configure(text_color=success)
        elif self.is_accepted:
            self.customer_lbl.configure(text_color=warning)
        self.load_btn = CTkButton(
            self,
            text=render_text("تحميل"),
            font=CTkFont(size=15, weight="bold"),
            command=self.load,
            fg_color=cyan_btn,
            hover_color=cyan_hover,
        )
        self.delete_btn = CTkButton(
            self,
            text=render_text("حذف"),
            font=CTkFont(size=15, weight="bold"),
            command=self.delete,
            fg_color=danger_btn,
            hover_color=danger_hover,
        )
        if self.owner_id != secretvars.owner_id:
            self.delete_btn.configure(state="disabled")
        self.customer_lbl.grid(row=0, column=2, sticky="nsew", padx=25)
        self.load_btn.grid(row=0, column=1, sticky="nsew", padx=25)
        self.delete_btn.grid(row=0, column=0, sticky="nsew", padx=50)

    def delete(self):
        Thread(
            target=lambda: asyncio.run(
                db.delete_customer(self.main_window, self, self.id)
            )
        ).start()

    def load(self):
        Thread(
            target=lambda: asyncio.run(
                db.get_data_of_account(self.main_window, self.id)
            )
        ).start()

    def disable(self):
        for child in self.winfo_children():
            child.configure(state="disabled")

    def enable(self):
        for child in self.winfo_children():
            child.configure(state="normal")
        if self.owner_id != secretvars.owner_id:
            self.delete_btn.configure(state="disabled")


class ToplevelWindow(CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("720x480")
        self.title("الحسابات اللتي حصلت غلي موافقة")
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        self.textbox = CTkTextbox(
            master=self,
            width=400,
            corner_radius=0,
            state="disabled",
            font=CTkFont(size=15),
        )
        self.textbox.grid(row=0, column=0, sticky="nsew")

    def add_account(self, account):
        if account in self.textbox.get("1.0", "end").split("\n"):
            return
        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"{account}\n")
        self.textbox.configure(state="disabled")
        self.textbox.see("end")


class AccountsManager(CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("720x480")
        self.title("اضافة الحسابات")
        self.rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.label1 = CTkLabel(
            self, text=render_text("الحسابات"), font=CTkFont(size=15)
        )
        self.label1.grid(row=0, column=0, sticky="nsew")
        self.textbox = CTkTextbox(
            master=self, width=400, corner_radius=0, font=CTkFont(size=15)
        )
        self.textbox.grid(row=1, column=0, sticky="nsew", pady=10)
        self.label2 = CTkLabel(
            self, text=render_text("كلمة المرور"), font=CTkFont(size=15)
        )
        self.label2.grid(row=2, column=0, sticky="nsew")
        self.entry = CTkEntry(self, width=400, font=CTkFont(size=15))
        self.entry.grid(row=3, column=0, sticky="nsew", pady=10)
        self.add_btn = CTkButton(
            self,
            text=render_text("اضافة"),
            font=CTkFont(size=15),
            command=self.get_accounts,
        )
        self.add_btn.grid(row=4, column=0, sticky="nsew", pady=10)

    def get_accounts(self):
        if not self.textbox.get("1.0", "end").strip():
            messagebox.showerror("خطأ", "الرجاء ادخال الحسابات")
            return
        if not self.entry.get():
            messagebox.showerror("خطأ", "الرجاء ادخال كلمة المرور")
            return
        self.entry.configure(state="disabled")
        self.textbox.configure(state="disabled")
        self.add_btn.configure(state="disabled")
        accounts = [
            account for account in self.textbox.get("1.0", "end").split("\n") if account
        ]
        for account in accounts:
            self.master.add_applicant(account, self.entry.get().strip(), False)
        self.destroy()
        return


class FillData(CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("900x480")
        self.title("اضافة الحسابات")
        self.main_window = self.master
        self.account_obj = None

        self.documents = (
            {"passport": [None, 100]}
            if self.main_window.visa_id != 3
            else {
                "nulla": [None, 187],
                "passport": [None, 100],
                "phoneNumber": [None, 188],
            }
        )

        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")
        self.default_width = 100

        self.email_lbl = CTkLabel(self, text=render_text("اسم المستخدم/الايميل"))
        self.email_lbl.grid(row=0, column=2, sticky="nsew")
        self.email_entry = CTkEntry(
            master=self, width=self.default_width, placeholder_text="Email/Username"
        )
        self.email_entry.grid(row=0, column=1, sticky="nsew", padx=30, pady=5)
        self.password_lbl = CTkLabel(self, text=render_text("كلمة المرور"))
        self.password_lbl.grid(row=1, column=2, sticky="nsew")
        self.password_entry = CTkEntry(
            master=self, width=self.default_width, show="*", placeholder_text="Password"
        )
        self.password_entry.grid(row=1, column=1, sticky="nsew", padx=30, pady=5)
        self.gender_pick_lbl = CTkLabel(self, text=render_text("الجنس"))
        self.gender_pick_lbl.grid(row=2, column=2, sticky="nsew")
        self.gender_pick_options = ["ذكر", "انثى"]
        self.gender_pick = CTkOptionMenu(
            master=self, values=self.gender_pick_options, width=self.default_width
        )
        self.gender_pick.grid(row=2, column=1, sticky="nsew", padx=30, pady=5)
        self.residence_address_lbl = CTkLabel(self, text=render_text("عنوان السكن"))
        self.residence_address_lbl.grid(row=3, column=2, sticky="nsew")
        self.residence_address_entry = CTkEntry(
            master=self, width=self.default_width, placeholder_text="Menoufia"
        )
        self.residence_address_entry.grid(
            row=3, column=1, sticky="nsew", padx=30, pady=5
        )
        self.passport_issue_date_lbl = CTkLabel(
            self, text=render_text("تاريخ اصدار الباسبور")
        )
        self.passport_issue_date_lbl.grid(row=4, column=2, sticky="nsew")
        self.passport_issue_date_entry = CTkEntry(
            master=self, width=self.default_width, placeholder_text="YYYY-MM-DD"
        )
        self.passport_issue_date_entry.grid(
            row=4, column=1, sticky="nsew", padx=30, pady=5
        )
        self.passport_expiry_date_lbl = CTkLabel(
            self, text=render_text("تاريخ انتهاء الباسبور")
        )
        self.passport_expiry_date_lbl.grid(row=5, column=2, sticky="nsew")
        self.passport_expiry_date_entry = CTkEntry(
            master=self, width=self.default_width, placeholder_text="YYYY-MM-DD"
        )
        self.passport_expiry_date_entry.grid(
            row=5, column=1, sticky="nsew", padx=30, pady=5
        )
        self.passport_img_lbl = CTkLabel(self, text=render_text("صورة الجواز"))
        self.passport_img_lbl.grid(row=6, column=2, sticky="nsew")
        self.passport_img_btn = CTkButton(
            self,
            text=render_text("تحميل"),
            width=self.default_width,
            fg_color=primary_btn,
            hover_color=primary_hover,
            command=lambda: self.browse_file("passport"),
        )
        self.passport_img_btn.grid(row=6, column=1, sticky="nsew", padx=30, pady=5)
        self.passport_img_status = CTkLabel(
            self, text=render_text("غير موجود"), text_color=danger
        )
        self.passport_img_status.grid(row=6, column=0, sticky="nsew")

        if self.main_window.visa_id == 3:

            self.nulla_img_lbl = CTkLabel(self, text=render_text("صورة العقد"))
            self.nulla_img_lbl.grid(row=7, column=2, sticky="nsew")
            self.nulla_img_btn = CTkButton(
                self,
                text=render_text("تحميل"),
                width=self.default_width,
                fg_color=primary_btn,
                hover_color=primary_hover,
                command=lambda: self.browse_file("nulla"),
            )
            self.nulla_img_btn.grid(row=7, column=1, sticky="nsew", padx=30, pady=5)
            self.phone_img_lbl = CTkLabel(self, text=render_text("صورة الهاتف"))
            self.phone_img_lbl.grid(row=8, column=2, sticky="nsew")
            self.phone_img_btn = CTkButton(
                self,
                text=render_text("تحميل"),
                width=self.default_width,
                fg_color=primary_btn,
                hover_color=primary_hover,
                command=lambda: self.browse_file("phoneNumber"),
            )
            self.phone_img_btn.grid(row=8, column=1, sticky="nsew", padx=30, pady=5)

            self.nulla_img_status = CTkLabel(
                self, text=render_text("غير موجود"), text_color=danger
            )
            self.nulla_img_status.grid(row=7, column=0, sticky="nsew")

            self.phonenum_img_status = CTkLabel(
                self, text=render_text("غير موجود"), text_color=danger
            )
            self.phonenum_img_status.grid(row=8, column=0, sticky="nsew")

        self.add_btn = CTkButton(
            self,
            text=render_text("اضافة"),
            width=self.default_width,
            command=self.collect_data,
        )
        self.add_btn.grid(row=9, column=1, sticky="nsew", pady=50)

    def collect_data(self):
        if not self.validate_data():
            messagebox.showerror("خطأ", "الرجاء التأكد من ملء جميع الحقول")
            return
        data = {
            "documents": self.documents,
            "username": self.email_entry.get(),
            "password": self.password_entry.get(),
            "gender": "M" if self.gender_pick.get() == "ذكر" else "F",
            "residence_address": self.residence_address_entry.get(),
            "passport_issue_date": self.passport_issue_date_entry.get(),
            "passport_expiry_date": self.passport_expiry_date_entry.get(),
        }
        if self.account_obj:
            self.account_obj.data = data
            self.account_obj.name.set(data["username"])
            self.account_obj.password.set(data["password"])
            self.account_obj = None
            self.destroy()
            return
        self.main_window.recieve_data_from_fillData(data)
        self.destroy()

    def browse_file(self, type, file_path=None, should_pop_up=True):
        if should_pop_up:
            file_path = filedialog.askopenfilename(
                initialdir=os.curdir, title="Select a File"
            )
        if not (os.path.exists(file_path)):
            messagebox.showerror(
                title="خطأ",
                message="الملف {0} غير موجود".format(file_path.split("/")[-1]),
            )
            return
        self.documents[type][0] = file_path
        match type:
            case "passport":
                self.main_window.print_in_log("تم تحديد جواز السفر", color=info)
                self.passport_img_status.configure(
                    text=file_path.split("/")[-1], text_color=success
                )
                secretvars.data["media"]["passport"] = file_path
            case "nulla":
                self.main_window.print_in_log("تم تحديد صورة الهوية", color=info)
                self.nulla_img_status.configure(
                    text=file_path.split("/")[-1], text_color=success
                )
                secretvars.data["media"]["nulla"] = file_path
            case "phoneNumber":
                self.main_window.print_in_log("تم تحديد رقم الهاتف", color=info)
                self.phonenum_img_status.configure(
                    text=file_path.split("/")[-1], text_color=success
                )
                secretvars.data["media"]["phoneNumber"] = file_path

    def validate_data(self):
        for i in self.documents:
            if self.documents[i][0] == None:
                print(i)
                return False
        for child in self.winfo_children():
            if isinstance(child, CTkEntry):
                if child.get() == "":
                    return False
        return True

    def update_data(self, data, account_obj=None):
        self.account_obj = account_obj
        self.email_entry.insert(0, data["username"])
        self.password_entry.insert(0, data["password"])
        self.residence_address_entry.insert(0, data["residence_address"])
        self.passport_issue_date_entry.insert(0, data["passport_issue_date"])
        self.passport_expiry_date_entry.insert(0, data["passport_expiry_date"])
        self.gender_pick.set(
            render_text("ذكر") if data["gender"] == "M" else render_text("انثي")
        )
        for key in data["documents"]:
            if data["documents"][key][0]:
                self.browse_file(key, data["documents"][key][0], False)


class BookDataView(CTkToplevel):
    def __init__(self, master, data,*args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.frames = []
        self.resizable(False, False)
        self.geometry("1024x400")
        self.title("بيانات خاصة بالحجز")
        self.grid_columnconfigure(0, weight=1)
        self.ex_data = data
        
        for data in self.ex_data:
            frame_test = DataView(self, data, self.ex_data[data])
            frame_test.grid(row=len(self.frames), column=0, sticky="nsew", pady=5)
            self.frames.append(frame_test)


class DataView(CTkFrame):
    def __init__(self, master, key, value, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")
        self.key = key
        self.value = value
        self.btn_var = StringVar(self, render_text("نسخ"))

        self.key_lbl = CTkLabel(self, text=self.key, font=CTkFont(size=15))
        self.key_lbl.grid(row=0, column=0, sticky="nsew", padx=5)

        self.value_lbl = CTkLabel(
            self,
            text=self.value if self.value else str(self.value),
            font=CTkFont(size=15),
        )
        self.value_lbl.grid(row=0, column=1, sticky="nsew", padx=25)

        self.copy_btn = CTkButton(
            self,
            textvariable=self.btn_var,
            font=CTkFont(size=15),
            command=self.copy_action,
            fg_color=primary_btn,
            hover_color=primary_hover,
            
        )
        
        self.copy_btn.grid(row=0, column=2, sticky="nsew", padx=50)
        if self.key == "AccountEmail":
            self.copy_btn.configure(state="disabled")
        
        
    
    def copy_action(self):
        self.btn_var.set(render_text("تم النسخ!"))
        self.copy_btn.configure(
            fg_color="#22bb33", state="disabled", text_color="#ffffff"
        )
        self.master.clipboard_clear()
        self.master.clipboard_append(self.value)
        self.after(1000, lambda: self.btn_var.set(render_text("نسخ")))
        self.after(
            1000,
            lambda: self.copy_btn.configure(
                fg_color=primary_btn, state="normal", text_color="#DCE4EE"
            ),
        )
        
