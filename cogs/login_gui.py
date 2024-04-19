from customtkinter import *
from .login_manager import check_login
from .colors import *
import asyncio
from .utility import resource_path
from threading import Thread
from tkinter import messagebox
from .gui import Window
from awesometkinter.bidirender import render_text



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
        self.progress_bar = CTkProgressBar(self, mode="indeterminate", indeterminate_speed=1)
        self.progress_bar.start()
        self.progress_bar.place(relx=0.4, rely=0.85, anchor=CENTER)
        
        self.status = CTkLabel(self, text="", font=CTkFont(family="Segoe UI", size=15))
        self.status.place(relx=0.5, rely=0.1, anchor=CENTER)

    def submit(self):
        if self.validation():
            self.disable()
            self.status.configure(text=render_text("جاري التحقق"), text_color=info)
            thread = Thread(target=lambda : asyncio.run(check_login(self.username_entry.get(), self.password_entry.get(), self)))
            thread.start()
        
    def validation(self):
        if (
            self.username_entry.get() == ""
            or self.password_entry.get() == ""
        ):
            messagebox.showerror(title="خطأ", message="برجاء تعبئة جميع الحقول")
            return False
        return True

    def disable(self):
        self.username_entry.configure(state="disabled")
        self.password_entry.configure(state="disabled")
        self.submit_btn.configure(state="disabled")
        
    def enable(self):
        self.username_entry.configure(state="normal")
        self.password_entry.configure(state="normal")
        self.submit_btn.configure(state="normal")
    
    def destroy_login(self):
        for child in self.winfo_children():
            child.destroy()
    
    def init_canva(self):
        self.destroy_login()
        frame = Window(self)
        frame.grid(sticky="nsew")
        self.geometry("720x480")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        