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
from .sheet_management import initialize_sheet


class App2(CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.count = 0
        self.labels = []
        self.applicant = None
        self.applicants = []
        self.bot = None
        self.start_delay = None
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
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.navigation_frame = CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(6, weight=1)

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

        self.frame_2_button = CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text=render_text("معلومات العميل"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.frame_2_button_event,
        )
        self.frame_2_button.grid(row=3, column=0, sticky="ew")

        self.frame_3_button = CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text=render_text("المستندات"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.frame_3_button_event,
        )
        self.frame_3_button.grid(row=4, column=0, sticky="ew")
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
        self.frame_5_button.grid(row=5, column=0, sticky="ew")

        self.home_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.third_frame = CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.fourth_frame = CTkScrollableFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.fifth_frame = CTkScrollableFrame(
            self, corner_radius=0, fg_color="transparent"
        )

        self.select_frame_by_name("home")
        for frame in [self.home_frame, self.second_frame, self.third_frame]:
            frame.grid_columnconfigure(0, weight=4, minsize=5)
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_columnconfigure(2, weight=4)

        self.fifth_frame.grid_columnconfigure(0, weight=5)
        self.fourth_frame.grid_columnconfigure(0, weight=5)

        ###############################  HOME_FRAME #####################################

        self.username_label = CTkLabel(
            self.home_frame, text=render_text("اسم المستخدم")
        )
        self.username_label.grid(row=0, column=2, sticky="nsew")
        self.username_entry = CTkEntry(self.home_frame, width=170)
        self.username_entry.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.password_label = CTkLabel(self.home_frame, text=render_text("كلمة المرور"))
        self.password_label.grid(row=1, column=2, sticky="nsew")
        self.password_entry = CTkEntry(self.home_frame, show="*", width=170)
        self.password_entry.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.add_applicant_btn = CTkButton(
            self.home_frame,
            width=170,
            text=render_text("اضافة مستخدم"),
            command=lambda: self.add_applicant(
                self.username_entry.get(), self.password_entry.get()
            ),
        )
        self.add_applicant_btn.grid(row=2, column=1, sticky="s", padx=5, pady=5)
        self.save_password_check = StringVar(value="on")
        self.start_with_timer_check = StringVar(value="on")
        self.save_password = CTkCheckBox(
            self.home_frame,
            text=render_text("حفظ كلمة المرور"),
            variable=self.save_password_check,
            onvalue="on",
            offvalue="off",
        )
        self.save_password.grid(row=2, column=0, sticky="s", padx=5, pady=5)

        self.start_with_timer_lbl = CTkLabel(
            self.home_frame, text=render_text("بدء الساعة التاسعة صباحا")
        )

        self.office_id_lbl = CTkLabel(self.home_frame, text=render_text("المكتب"))
        self.office_id_lbl.grid(row=3, column=2, sticky="s", padx=5, pady=5)
        self.office_id_option = CTkOptionMenu(
            self.home_frame, values=["Cairo", "Alexandria"], width=170
        )
        self.office_id_option.grid(row=3, column=1, sticky="s", padx=5, pady=5)
        
        self.visa_price_lbl = CTkLabel(self.home_frame, text=render_text("سعر الفيزا"))
        self.visa_price_lbl.grid(row=4, column=2, sticky="s", padx=5, pady=5)
        self.visa_price_options = CTkOptionMenu(
            self.home_frame, values=["Standard - EGP 1750", "Vip - EGP 3810"], width=170
        )
        self.visa_price_options.grid(row=4, column=1, sticky="s", padx=5, pady=5)
        
        self.mode_lbl = CTkLabel(self.home_frame, text=render_text("الوضع"))
        self.mode_lbl.grid(row=5, column=2, sticky="s", padx=5, pady=5)
        self.mode_option = CTkOptionMenu(
            self.home_frame, values=[render_text("استكمال حجز"), render_text("البحث عن حجز")], width=170
        )
        self.mode_option.grid(row=5, column=1, sticky="s", padx=5, pady=5)
        
        
        
        self.start_with_timer_lbl.grid(row=6, column=2, sticky="s", padx=5, pady=5)
        self.start_with_timer_switch = CTkSwitch(
            self.home_frame,
            text="",
            variable=self.start_with_timer_check,
            onvalue="on",
            offvalue="off",
        )
        self.start_with_timer_switch.grid(row=6, column=1, sticky="s", padx=5, pady=5)

        self.start_program_button = CTkButton(
            self.home_frame,
            text=render_text("بدا البرنامج"),
            command=self.start_execution,
        )
        self.start_program_button.grid(row=8, column=2, sticky="s", padx=5, pady=5)
        self.home_disable_btn = CTkButton(
            self.home_frame,
            text=render_text("تعطيل البرنامج"),
            command=self.stop_execution,
            state="disabled",
        )
        self.home_disable_btn.grid(row=8, column=0, sticky="s", padx=5, pady=5)

        #############################  ACCOUNT_INFORMATION ######################################
        self.birthdate_lbl = CTkLabel(
            self.second_frame, text=render_text("تاريخ الميلاد")
        )
        self.birthdate_lbl.grid(row=2, column=2, sticky="nsew")
        self.birthdate_entry = CTkEntry(
            self.second_frame, placeholder_text="YYYY-MM-DD"
        )
        self.birthdate_entry.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        self.gender_lbl = CTkLabel(self.second_frame, text=render_text("الجنس"))
        self.gender_lbl.grid(row=3, column=2, sticky="nsew")
        self.gender_entry = CTkOptionMenu(self.second_frame, values=["ذكر", "انثى"])
        self.gender_entry.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)
        self.residenceAddress_lbl = CTkLabel(
            self.second_frame, text=render_text("عنوان السكن")
        )
        self.residenceAddress_lbl.grid(row=4, column=2, sticky="nsew")
        self.residenceAddress_entry = CTkEntry(
            self.second_frame, placeholder_text="menofia"
        )
        self.residenceAddress_entry.grid(row=4, column=1, sticky="nsew", padx=5, pady=5)
        self.passportNumber_lbl = CTkLabel(
            self.second_frame, text=render_text("رقم الجواز")
        )
        self.passportNumber_lbl.grid(row=5, column=2, sticky="nsew")
        self.passportNumber_entry = CTkEntry(
            self.second_frame, placeholder_text="A123456789"
        )
        self.passportNumber_entry.grid(row=5, column=1, sticky="nsew", padx=5, pady=5)
        self.passportDateOfIssue_lbl = CTkLabel(
            self.second_frame, text=render_text("تاريخ الاصدار")
        )
        self.passportDateOfIssue_lbl.grid(row=6, column=2, sticky="nsew")
        self.passportDateOfIssue_entry = CTkEntry(
            self.second_frame, placeholder_text="YYYY-MM-DD"
        )
        self.passportDateOfIssue_entry.grid(
            row=6, column=1, sticky="nsew", padx=5, pady=5
        )
        self.passportDateOfExpiry_lbl = CTkLabel(
            self.second_frame, text=render_text("تاريخ الانتهاء")
        )
        self.passportDateOfExpiry_lbl.grid(row=7, column=2, sticky="nsew")
        self.passportDateOfExpiry_entry = CTkEntry(
            self.second_frame, placeholder_text="YYYY-MM-DD"
        )
        self.passportDateOfExpiry_entry.grid(
            row=7, column=1, sticky="nsew", padx=5, pady=5
        )

        self.save_button = CTkButton(
            self.second_frame, text=render_text("حفظ"), command=self.get_data
        )
        self.save_button.grid(row=10, column=2, sticky="s", padx=5, pady=5)
        self.applicant_edit_btn = CTkButton(
            self.second_frame,
            text=render_text("تعديل"),
            command=self.enable_applcant_data,
            state="disabled",
        )
        self.applicant_edit_btn.grid(row=10, column=0, sticky="s", padx=5, pady=5)
        ############################ IMG ##############################################

        self.passport_img_lbl = CTkLabel(
            self.third_frame, text=render_text("صورة الجواز")
        )
        self.passport_img_lbl.grid(row=0, column=2, sticky="nsew")
        self.passport_img_btn = CTkButton(
            self.third_frame,
            text=render_text("تحميل"),
            command=lambda: self.browse_file("passport"),
        )
        self.passport_img_btn.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.passport_img_state = CTkLabel(
            self.third_frame, text=render_text("لم يتم تحميل الصورة"), text_color=danger
        )
        self.passport_img_state.grid(row=0, column=0, sticky="nsew")

        self.nulla_img_lbl = CTkLabel(self.third_frame, text=render_text("صورة الهوية"))
        self.nulla_img_btn = CTkButton(
            self.third_frame,
            text=render_text("تحميل"),
            command=lambda: self.browse_file("nulla"),
        )
        self.nulla_img_btn.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.nulla_img_lbl.grid(row=1, column=2, sticky="nsew")
        self.nulla_img_state = CTkLabel(
            self.third_frame, text=render_text("لم يتم تحميل الصورة"), text_color=danger
        )
        self.nulla_img_state.grid(row=1, column=0, sticky="nsew")
        self.phonenum_img_lbl = CTkLabel(
            self.third_frame, text=render_text("صورة رقم الهاتف")
        )
        self.phonenum_img_btn = CTkButton(
            self.third_frame,
            text=render_text("تحميل"),
            command=lambda: self.browse_file("phoneNumber"),
        )
        self.phonenum_img_btn.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        self.phonenum_img_lbl.grid(row=2, column=2, sticky="nsew")
        self.phonenum_img_state = CTkLabel(
            self.third_frame, text=render_text("لم يتم تحميل الصورة"), text_color=danger
        )
        self.phonenum_img_state.grid(row=2, column=0, sticky="nsew")
        self.img_save_button = CTkButton(
            self.third_frame, text=render_text("حفظ"), command=self.save_img_data
        )
        self.img_save_button.grid(row=3, column=2, sticky="s", padx=5, pady=5)
        self.img_edit_button = CTkButton(
            self.third_frame,
            text=render_text("تعديل"),
            command=self.edit_img_data,
            state="disabled",
        )
        self.img_edit_button.grid(row=3, column=0, sticky="s", padx=5, pady=5)

        #############################ACCOUNTS FRAME######################################
        self.account_test = AccountFrame(
            "Account Name", "Account Password", True, self.fourth_frame
        )
        self.account_test.grid(
            row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5
        )
        #############################################################################

        self.home_frame.grid_rowconfigure(8, weight=1)
        self.second_frame.grid_rowconfigure(10, weight=1)
        self.third_frame.grid_rowconfigure(3, weight=1)

        #############################################################################

        for frame in (self.home_frame, self.second_frame):
            for child in frame.winfo_children():
                if isinstance(child, CTkEntry):
                    child.bind("<Button-3>", self.right_click_event)

    def select_frame_by_name(self, name):
        self.home_button.configure(
            fg_color=("gray75", "gray25") if name == "home" else "transparent"
        )
        self.frame_2_button.configure(
            fg_color=("gray75", "gray25") if name == "frame_2" else "transparent"
        )
        self.frame_3_button.configure(
            fg_color=("gray75", "gray25") if name == "frame_3" else "transparent"
        )
        self.frame_5_button.configure(
            fg_color=("gray75", "gray25") if name == "frame_5" else "transparent"
        )
        self.frame_4_button.configure(
            fg_color=("gray75", "gray25") if name == "frame_4" else "transparent"
        )

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

    def frame_4_button_event(self):
        self.select_frame_by_name("frame_4")

    def add_applicant(self, account_name, account_password):
        if not (self.validation(self.home_frame)):
            messagebox.showerror(title="خطأ", message="برجاء تحديد جميع الحقول")
            return
        account_test = AccountFrame(
            account_name, account_password, False, self.fourth_frame
        )
        account_test.grid(
            row=len(self.applicants) + 1,
            column=0,
            columnspan=3,
            sticky="nsew",
            padx=5,
            pady=5,
        )
        self.applicants.append(account_test)
        self.print_in_log(f"تم حفظ {account_name} بنجاح", color=info)
        self.username_entry.delete(0, "end")
        if self.save_password_check.get() == "off":
            self.password_entry.delete(0, "end")
        self.username_entry.focus()

    def get_data(self):
        if not self.validation(self.second_frame):
            messagebox.showerror(title="خطأ", message="برجاء تعبئة جميع الحقول")
            return
        data = {
            "birthDate": "",
            "residenceAddress": "",
            "passportNumber": "",
            "passportDateOfIssue": "",
            "passportDateOfExpiry": "",
            "gender": "M" if self.gender_entry.get() == "ذكر" else "F",
            "visa_id": str(self.visa_id),
        }
        selected_data = []
        for child in self.second_frame.winfo_children():
            if isinstance(child, CTkEntry):
                selected_data.append(child.get())
        for i in range(len(selected_data)):
            data[list(data.keys())[i]] = selected_data[i]

        self.applicant = Applicant(**data)
        self.disable_applcant_data()
        self.print_in_log("تم تحديد بيانات المستخدم", color=success)

    def disable_applcant_data(self):
        for child in self.second_frame.winfo_children():
            if (
                isinstance(child, CTkEntry)
                or isinstance(child, CTkButton)
                or isinstance(child, CTkOptionMenu)
            ):
                child.configure(state="disabled")
        self.applicant_edit_btn.configure(state="normal")

    def enable_applcant_data(self):
        for child in self.second_frame.winfo_children():
            if (
                isinstance(child, CTkEntry)
                or isinstance(child, CTkButton)
                or isinstance(child, CTkOptionMenu)
            ):
                child.configure(state="normal")
        self.applicant_edit_btn.configure(state="disabled")

    def validation(self, frame):
        for child in frame.winfo_children():
            if isinstance(child, CTkEntry):
                if child.get() == "":
                    return False
        return True

    def browse_file(self, type):
        file_path = filedialog.askopenfilename(
            initialdir=os.curdir, title="Select a File"
        )
        self.documents[type][0] = file_path
        match type:
            case "passport":
                self.print_in_log("تم تحديد جواز السفر", color=info)
                self.passport_img_state.configure(
                    text=file_path.split("/")[-1], text_color=success
                )
            case "nulla":
                self.print_in_log("تم تحديد صورة الهوية", color=info)
                self.nulla_img_state.configure(
                    text=file_path.split("/")[-1], text_color=success
                )
            case "phoneNumber":
                self.print_in_log("تم تحديد رقم الهاتف", color=info)
                self.phonenum_img_state.configure(
                    text=file_path.split("/")[-1], text_color=success
                )

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
            self.enable_applcant_data()
            self.enbale_home_data()
            self.edit_img_data()
            secretvars.MAIN_FLAG = 0
            self.enbale_home_data()

    def start_execution(self):
        if not (self.validate_all_fields()):
            return
        self.disable_home_data()
        if self.start_with_timer_check.get() == "on":
            countdown = Countdown(7, 59, 55)
            self.start_delay = self.after(
                countdown.time_to_start_program(), self.bot_excution
            )
            self.print_in_log(f"البرنامج سيبدأ في {countdown}", color=warning)
        else:
            self.bot_excution()
        self.select_frame_by_name("frame_5")
        

    def bot_excution(self):
        secretvars.MAIN_FLAG = 1
        self.save_img_data()
        self.get_data()
        self.bot = Bot(
            self,
            self.applicant,
            self.documents,
            self.office_id_option.get(),
            self.visa_id,
            0 if self.mode_option.get() == render_text("استكمال حجز") else 1,
            1 if self.visa_price_options.get() == "Standard - EGP 1750" else 2,
            self.start_with_timer_check.get() == "on"
        )
        self.bot.accounts = self.get_all_applicants()
        bot_thread = Thread(target=self.bot.start_booking)
        secretvars.Thread_Pool.append(bot_thread)
        bot_thread.start()
        if not(secretvars.FIRST_RUN):
            sheet = Thread(
                    target=initialize_sheet,
                    args=(secretvars.USERNAME, secretvars.PASSWORD),
                )
            secretvars.Thread_Pool.append(sheet)
            sheet.start()

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
        for key in self.documents:
            if not (self.documents[key][0]):
                messagebox.showerror(title="خطأ", message="برجاء تحديد جميع المستندات")
                self.select_frame_by_name("frame_3")
                return False
        if not (self.validation(self.second_frame)):
            self.select_frame_by_name("frame_2")
            messagebox.showerror(title="خطأ", message="برجاء تعبئة جميع البيانات")
            return False
        return True

    def get_all_applicants(self):
        return [applicant.get_applicant_data() for applicant in self.applicants]


class AccountFrame(CTkFrame):
    def __init__(self, name, password, hidden=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.password = password
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")

        self.account_name = CTkLabel(self, text=name, font=CTkFont(size=12))
        self.account_password = CTkLabel(self, text=password, font=CTkFont(size=12))
        self.account_name.grid(row=0, column=2, sticky="nsew", padx=25)
        self.account_password.grid(row=0, column=1, sticky="nsew", padx=25)
        if not (hidden):
            self.delet_btn = CTkButton(
                self,
                text=render_text("حذف"),
                command=self.delete,
                font=CTkFont(size=12),
                fg_color=danger_btn,
                hover_color=danger_hover,
            )
            self.delet_btn.grid(row=0, column=0, sticky="nsew", padx=50)

    def delete(self):
        self.master.master.master.master.applicants.remove(self)
        self.destroy()

    def get_applicant_data(self):
        return [self.name, self.password]
