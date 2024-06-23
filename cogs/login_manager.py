import psycopg
import bcrypt
import subprocess
from customtkinter import CTk
from tkinter import messagebox
from .colors import *
from awesometkinter.bidirender import render_text
from . import secretvars


def get_serial_num():
    result = subprocess.run(
        ["Wmic", "bios", "get", "serialnumber"], capture_output=True, text=True
    )
    return result.stdout.strip("\n").split("\n")[-1].strip(" ")

def get_baseboard_num():
    result = subprocess.run(
        ["Wmic", "baseboard", "get", "serialnumber"], capture_output=True, text=True
    )
    return result.stdout.strip("\n").split("\n")[-1].strip(" ")

async def check_login(username, password, window: CTk):
    try:
        async with await psycopg.AsyncConnection.connect(secretvars.URI) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM LOGIN WHERE username = %s", (username,)
                )
                user = await cursor.fetchone()
                if user:
                    if user[3]:
                        if bcrypt.checkpw(
                            password.encode("utf8"), user[2].encode("utf8")
                        ):
                            if user[-2] == None:
                                if get_serial_num():
                                    await cursor.execute(
                                        "UPDATE LOGIN SET HARDWARE_ID = %s WHERE username = %s",
                                        (
                                            get_baseboard_num(),
                                            username,
                                        ),
                                    )
                                    await db.commit()
                                    await cursor.execute(
                                        "UPDATE LOGIN SET attempts = attempts + 1 WHERE username = %s",
                                        (username,),
                                    )
                                await db.commit()
                                window.status.configure(
                                    text=render_text("تم تسجيل الدخول بنجاح"),
                                    text_color=success,
                                )
                                window.init_canva()
                                return
                            else:
                                if user[-2] == get_baseboard_num():
                                    await cursor.execute(
                                        "UPDATE LOGIN SET attempts = attempts + 1 WHERE username = %s",
                                        (username,),
                                    )
                                    await db.commit()
                                    window.status.configure(
                                        text=render_text("تم تسجيل الدخول بنجاح"),
                                        text_color=success,
                                    )
                                    window.init_canva()
                                    return
                window.enable()
                window.status.configure(
                    text=render_text("اسم المستخدم او كلمة المرور غير صحيحة"),
                    text_color=danger,
                )
                messagebox.showerror(
                    title="خطأ", message="اسم المستخدم او كلمة المرور غير صحيحة"
                )
                return
    except Exception as e:
        window.enable()
        window.status.configure(
            text=render_text("اسم المستخدم او كلمة المرور غير صحيحة"), text_color=danger
        )
        messagebox.showerror(
            title="خطأ", message="اسم المستخدم او كلمة المرور غير صحيحة"
        )
        return
