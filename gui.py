from customtkinter import *
from tkinter import messagebox
from datetime import datetime, timedelta
from almaviva_script import start_program
from customized_components import FloatSpinbox
from awesometkinter.bidirender import render_text
from threading import Thread
from colors import *


class Window(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self, parent)
        self.configure(height=400, width=400)
        self.restoring_function = None
        self.driver_thread = None
        label = CTkLabel(
            self, text="ALMAVIVA SCRIPT", font=CTkFont(family="Segoe UI", size=15)
        )
        label.place(relx=0.5, rely=0.1, anchor=CENTER)
        self.email_lbl = CTkLabel(
            self,
            text=render_text("اسم المستخدم"),
            font=CTkFont(family="Segoe UI", size=15),
        )
        self.email_lbl.place(relx=0.85, rely=0.25, anchor=E)
        self.email_entry = CTkEntry(self)
        self.email_entry.place(relx=0.5, rely=0.25, anchor=CENTER)
        self.password_lbl = CTkLabel(
            self,
            text=render_text("كلمة المرور"),
            font=CTkFont(family="Segoe UI", size=15),
        )
        self.password_lbl.place(relx=0.85, rely=0.32, anchor=E)
        self.password_entry = CTkEntry(self)
        self.password_entry.place(relx=0.5, rely=0.32, anchor=CENTER)
        self.label3 = CTkLabel(self, text="", font=CTkFont(size=20))
        self.label2 = CTkLabel(
            self, text="..", font=CTkFont(family="Segoe UI", size=15)
        )
        self.time_lbl = CTkLabel(
            self,
            text=render_text("وقت التنفيذ"),
            font=CTkFont(family="Segoe UI", size=15),
        )
        self.time_lbl.place(relx=0.85, rely=0.46, anchor=E)
        self.hours_lbl = CTkLabel(
            self, text=render_text("الساعة"), font=CTkFont(family="Segoe UI", size=13)
        )
        self.hours_lbl.place(relx=0.59, rely=0.4, anchor=CENTER)
        self.hours_entry = FloatSpinbox(self, width=100, step_size=1, max=12)
        self.hours_entry.place(relx=0.59, rely=0.46, anchor=CENTER)
        self.minutes_lbl = CTkLabel(
            self, text=render_text("الدقيقة"), font=CTkFont(family="Segoe UI", size=13)
        )
        self.minutes_lbl.place(relx=0.45, rely=0.4, anchor=CENTER)
        self.minutes_entry = FloatSpinbox(self, width=100, step_size=1, max=60)
        self.minutes_entry.place(relx=0.45, rely=0.46, anchor=CENTER)
        self.time_type = CTkOptionMenu(
            self, values=["ص", "م"], command=self.optionmenu_callback, width=50
        )
        self.time_type.place(relx=0.34, rely=0.46, anchor=CENTER)
        self.select_center_lbl = CTkLabel(
            self, text=render_text("المركز"), font=CTkFont(family="Segoe UI", size=15)
        )
        self.select_center_lbl.place(relx=0.82, rely=0.57, anchor=CENTER)
        self.select_center = CTkOptionMenu(
            self, values=["Cairo", "Alexandria"], command=self.optionmenu_callback
        )
        self.select_center.place(relx=0.5, rely=0.57, anchor=CENTER)
        self.select_destination_lbl = CTkLabel(
            self, text=render_text("الوجهة"), font=CTkFont(family="Segoe UI", size=15)
        )
        self.select_destination_lbl.place(relx=0.82, rely=0.72, anchor=CENTER)
        self.select_destination = CTkEntry(self, placeholder_text="italy or spain")
        self.select_destination.place(relx=0.5, rely=0.72, anchor=CENTER)
        self.select_trip_date_lbl = CTkLabel(
            self,
            text=render_text("يوم الرحلة"),
            font=CTkFont(family="Segoe UI", size=15),
        )
        self.select_trip_date_lbl.place(relx=0.82, rely=0.65, anchor=CENTER)
        self.select_trip_date = CTkOptionMenu(
            self, values=self.get_days_in_month(), command=self.optionmenu_callback
        )
        self.select_trip_date.place(relx=0.5, rely=0.645, anchor=CENTER)
        self.state_lbl = CTkLabel(
            self,
            text=render_text("انتظار..."),
            font=CTkFont(family="Segoe UI", size=13),
            text_color=info,
        )
        self.state_lbl.place(relx=0.2, rely=0.6, anchor=CENTER)
        self.start_program = CTkButton(
            self,
            text=render_text("بدأ البرنامج"),
            font=CTkFont(family="Segoe UI", size=15),
            command=lambda: self.update_timer(self.get_time()[0], self.get_time()[1]),
        )
        self.start_program.place(relx=0.6, rely=0.82, anchor=CENTER)
        self.stop_prgram = CTkButton(
            self,
            text=render_text("ايقاف البرنامج"),
            font=CTkFont(family="Segoe UI", size=15),
            command=lambda: self.update_timer(
                self.get_time()[0], self.get_time()[1], 0
            ),
            fg_color="#FF204E",
            hover_color="#A0153E",
            state=DISABLED,
        )
        self.stop_prgram.place(relx=0.4, rely=0.82, anchor=CENTER)
        self.components = [
            self.hours_entry,
            self.email_entry,
            self.minutes_entry,
            self.password_entry,
            self.time_type,
            self.select_trip_date,
            self.start_program,
            self.select_center,
            self.select_destination,
        ]

    def update_timer(self, det_h=0, det_min=0, condition=True):
        try:
            if condition:
                self.disable_components()
                current_date = datetime.now()
                next_date = current_date.replace(
                    hour=det_h, minute=det_min, second=5
                ) - (current_date + timedelta(days=1))
                hours, remainder = divmod(next_date.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                missing_time = "{0}:{1}:{2}".format(
                    (hours if hours >= 10 else "0" + str(hours)),
                    (minutes if minutes >= 10 else "0" + str(minutes)),
                    (seconds if seconds >= 10 else "0" + str(seconds)),
                )
                self.label2.configure(text=missing_time)
                self.label3.configure(
                    text=render_text("الوقت المتبقي حتي يتم تنفيذ البرنامج"),
                    text_color="white",
                )
                if hours == 0 and minutes == 0 and seconds == 0:
                    self.driver_thread = Thread(
                        target=start_program,
                        args=(
                            self.email_entry.get(),
                            self.password_entry.get(),
                            self.select_trip_date.get(),
                            self.select_center.get(),
                            self.select_destination.get(),
                            self,
                        ),
                    )
                    self.label3.configure(
                        text=render_text("البرنامج بدأ التنفيذ"),
                        font=("Muli", 17, "bold"),
                        text_color=success,
                    )
                    self.state_lbl.configure(
                        text=render_text("بدأت عملية التنفيذ بنجاح.."),
                        text_color=success,
                    )
                    self.restoring_function = self.after(100, self.driver_thread.start)
                    self.enable_components()
                else:
                    self.restoring_function = self.after(
                        1000, self.update_timer, det_h, det_min
                    )
            else:
                if self.restoring_function:
                    self.after_cancel(self.restoring_function)
                if self.driver_thread:
                    self.driver_thread.join()
                self.label2.configure(text="")
                self.label3.configure(
                    text=render_text("البرنامج توقف"), text_color="#FF204E"
                )
                self.enable_components()
            self.label3.place(relx=0.2, rely=0.25, anchor=CENTER)
            self.label2.place(relx=0.2, rely=0.31, anchor=CENTER)
        except Exception as e:
            print("Error occured just don't give a fuck")

    def get_time(self):
        hours, mins = [self.hours_entry.get(), self.minutes_entry.get()]
        if not (self.validation()):
            return
        if hours > 12 or hours == 0:
            messagebox.showerror(
                title="خطأ",
                message=" برجاء ادخال عدد الساعات بطريقة صحيحة حيث عدد الساعات ينحصر بين ال 1 الي 12",
            )
            return
        if mins >= 60:
            messagebox.showerror(
                title="خطأ",
                message=" برجاء ادخال عدد الساعات بطريقة صحيحة حيث عدد الدقائق ينحصر بين ال 0 الي 59",
            )
            return
        return (
            int(hours) % 12 if self.time_type.get() != "م" else (int(hours) + 12) % 24,
            int(mins),
        )

    def optionmenu_callback(self, choice):
        return choice

    def get_days_in_month(self):
        current_day = datetime.now()
        next_month = current_day.replace(month=current_day.month + 1)
        return list(
            map(str, range(current_day.day, (next_month - current_day).days + 1))
        )

    def disable_components(self):
        for component in self.components:
            try:
                component.configure(state=DISABLED)
            except:
                component.disable_component()
        self.stop_prgram.configure(state=NORMAL)

    def enable_components(self):
        for component in self.components:
            try:
                component.configure(state=NORMAL)
            except:
                component.enable_component()
        self.stop_prgram.configure(state=DISABLED)

    def validation(self):
        if (
            self.email_entry.get() == ""
            or self.password_entry.get() == ""
            or self.select_destination.get() == ""
        ):
            messagebox.showerror(title="خطأ", message="برجاء تعبئة جميع الحقول")
            return False
        return True
