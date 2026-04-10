from tkinter import filedialog
from tkinter import ttk
from enum import Enum
import tkinter as tk
import subprocess
import os.path
import json

CART_TYPES = ["rom", "bbram"]

class PicoStatus(Enum):
    NO_MPREMOTE = "Could not connect to Pico using 'mpremote'."
    NOT_FOUND_OR_NO_PERM = "Pico could not be found, or you are missing permissions to connect."
    PICO_FOUND = "Pico found."

def check_pico() -> PicoStatus:
    try:
        result = subprocess.run(
            ["mpremote", "ls"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return PicoStatus.NO_MPREMOTE

    if result.returncode == 1:
        return PicoStatus.NOT_FOUND_OR_NO_PERM
    else:
        return PicoStatus.PICO_FOUND

class CartFrame(tk.Frame):
    def __init__(self, master: tk.Widget, label: str, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self.label = tk.Label(self, text=label)
        self.label.grid(row=0, column=0)

        self.cart_type = ttk.Combobox(self, values=CART_TYPES)
        self.cart_type.current(0)
        self.cart_type.grid(row=0, column=1)

        self.file_btn = tk.Button(self, text="<Empty>", command=self.change_file)
        self.file_btn.grid(row=0, column=2)

        self.file = None

    def change_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select a Cartridge",
            initialdir="./bin",
            filetypes=[
                ("Binary files", "*"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_btn.config(text=os.path.basename(file_path))
            self.file = file_path
        else:
            self.file_btn.config(text="<Empty>")
            self.file = None
    
    def get(self) -> tuple[str, str]|None:
        cart_type = self.cart_type.get()

        if cart_type is None or self.file is None:
            return None
        return (cart_type, self.file)

class App(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.title("Picopex CartSwap")
        self.resizable(False, False)
        self.geometry("1000x225")

        self.status = tk.Label(self, text="")
        self.show_status()
        self.status.pack()
        
        self.cs1Frame = CartFrame(self, label="CS1: ")
        self.cs1Frame.pack()
        self.cs2Frame = CartFrame(self, label="CS2: ")
        self.cs2Frame.pack()

        self.install_btn = tk.Button(self, text="Install Cartridges", command=self.install)
        self.install_btn.pack()

    def show_status(self) -> None:
        self.status.config(text=check_pico().value)
        self.after(2000, self.show_status)

    def install(self) -> None:
        self.show_status()
        status = check_pico()

        if status != PicoStatus.PICO_FOUND:
            tk.messagebox.showerror("Error", status.value)
            return
        
        cs1 = self.cs1Frame.get()
        cs2 = self.cs2Frame.get()
        
        with open("_cartridges.json", "w") as f:
            json.dump([cs1[0] if cs1 else None, cs2[0] if cs2 else None], f)
        subprocess.run(["mpremote", "cp", "_cartridges.json", ":/cartridges.json"])
        os.remove("_cartridges.json")

        for i, cs in enumerate([cs1, cs2]):
            if not cs: continue
            cart_type, path = cs

            target = f":/cs{i+1}.bin"
            subprocess.run(["mpremote", "cp", path, target])
        
        print("resetting...")
        subprocess.run(["mpremote", "soft-reset"])
        print("done.")
        self.status.config(text="Installed.")

if __name__ == "__main__":
    App().mainloop()
