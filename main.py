from cogs.gui import Window
from customtkinter import CTk
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    root = CTk()
    root.title("ALMAVIVA SCRIPT")
    frame = Window(root)
    frame.grid(sticky="nsew")
    root.geometry("720x480")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.iconbitmap(resource_path("thunder.ico"))
    root.mainloop()
