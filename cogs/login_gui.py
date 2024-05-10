from customtkinter import *
from .login_manager import check_login
from .colors import *
import asyncio
from .utility import resource_path
from threading import Thread
from tkinter import messagebox
from awesometkinter.bidirender import render_text
from . import secretvars
from .sheet_management import initialize_sheet
from . import gui


class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FLAG = 0
        self.geometry("320x200")
        self.iconbitmap(resource_path("thunder.ico"))
        self.title("ALMAVIVA SCRIPT")
        self.username_lbl = CTkLabel(self, text="Username")
        self.username_entry = CTkEntry(self)
        self.username_lbl.place(relx=0.8, rely=0.3, anchor=CENTER)
        self.username_entry.place(relx=0.4, rely=0.3, anchor=CENTER)
        self.password_lbl = CTkLabel(self, text="Password")
        self.password_entry = CTkEntry(self, show="*")
        self.password_lbl.place(relx=0.8, rely=0.5, anchor=CENTER)
        self.password_entry.place(relx=0.4, rely=0.5, anchor=CENTER)

        self.submit_btn = CTkButton(self, text="Submit", command=self.submit)
        self.submit_btn.place(relx=0.4, rely=0.7, anchor=CENTER)
        self.progress_bar = CTkProgressBar(
            self, mode="indeterminate", indeterminate_speed=1
        )
        self.progress_bar.start()
        self.progress_bar.place(relx=0.4, rely=0.85, anchor=CENTER)

        self.status = CTkLabel(self, text="", font=CTkFont(family="Segoe UI", size=15))
        self.status.place(relx=0.5, rely=0.1, anchor=CENTER)
        self.bind("<Return>", self.submit)
        self.init_canva()

    def submit(self, event=None):
        if self.validation():
            self.disable()
            self.status.configure(text=render_text("جاري التحقق"), text_color=info)
            thread = Thread(
                target=lambda: asyncio.run(
                    check_login(
                        self.username_entry.get(), self.password_entry.get(), self
                    )
                )
            )
            secretvars.Thread_Pool.append(thread)
            thread.start()

    def validation(self):
        if self.username_entry.get() == "" or self.password_entry.get() == "":
            messagebox.showerror(title="خطأ", message="برجاء تعبئة جميع الحقول")
            return False
        return True

    def disable(self):
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.submit_btn.configure(state="disabled")

    def enable(self):
        try:
            self.username_entry.configure(state="normal")
            self.password_entry.configure(state="normal")
            self.submit_btn.configure(state="normal")
        except:
            pass

    def destroy_login(self):
        try:
            sheet = Thread(
                target=initialize_sheet,
                args=(self.username_entry.get(), self.password_entry.get()),
            )
            secretvars.Thread_Pool.append(sheet)
            sheet.start()
            for child in self.winfo_children():
                child.destroy()
        except Exception as e:
            pass

    def init_canva(self):
        self.bind("<Return>", lambda e: "break")
        self.destroy_login()
        self.geometry("960x480")
        frame = gui.App2(self)
        frame.pack(side="top", fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
