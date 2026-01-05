import customtkinter
import customtkinter as ctk
import tkinter as tk
import os
import sys
import ctypes

# ================= BIN HASH =================

def bin_hash_prefix(text: str) -> int:
    data = text.encode("latin-1")
    h = 0xFFFFFFFF
    for b in data:
        h = (h * 0x21 + b) & 0xFFFFFFFF
    return h

# ================= VLT HASH =================
def u32(x):
    return x & 0xFFFFFFFF

def mix32_1(a, b, c):
    a = u32((c >> 13) ^ (a - b - c))
    b = u32((a << 8) ^ (b - c - a))
    c = u32((b >> 13) ^ (c - a - b))

    a = u32((c >> 12) ^ (a - b - c))
    b = u32((a << 16) ^ (b - c - a))
    c = u32((b >> 5) ^ (c - a - b))

    a = u32((c >> 3) ^ (a - b - c))
    b = u32((a << 10) ^ (b - c - a))
    c = u32((b >> 15) ^ (c - a - b))

    return a, b, c

def mix32_2(a, b, c):
    a = u32((c >> 13) ^ (a - b - c))
    b = u32((a << 8) ^ (b - c - a))
    c = u32((b >> 13) ^ (c - a - b))

    a = u32((c >> 12) ^ (a - b - c))
    b = u32((a << 16) ^ (b - c - a))
    c = u32((b >> 5) ^ (c - a - b))

    a = u32((c >> 3) ^ (a - b - c))
    b = u32((a << 10) ^ (b - c - a))

    return u32((b >> 15) ^ (c - a - b))

def vlt_hash_32(text: str) -> int:
    if not text:
        return 0

    arr = text.encode("ascii", errors="ignore")

    a = 0x9E3779B9
    b = 0x9E3779B9
    c = 0xABCDEF00

    v1 = 0
    v2 = len(arr)

    while v2 >= 12:
        a = u32(a + int.from_bytes(arr[v1:v1+4], "little"))
        b = u32(b + int.from_bytes(arr[v1+4:v1+8], "little"))
        c = u32(c + int.from_bytes(arr[v1+8:v1+12], "little"))

        a, b, c = mix32_1(a, b, c)

        v1 += 12
        v2 -= 12

    c = u32(c + len(arr))

    if v2 == 11:
        c = u32(c + (arr[v1 + 10] << 24))
    if v2 >= 10:
        c = u32(c + (arr[v1 + 9] << 16))
    if v2 >= 9:
        c = u32(c + (arr[v1 + 8] << 8))
    if v2 >= 8:
        b = u32(b + (arr[v1 + 7] << 24))
    if v2 >= 7:
        b = u32(b + (arr[v1 + 6] << 16))
    if v2 >= 6:
        b = u32(b + (arr[v1 + 5] << 8))
    if v2 >= 5:
        b = u32(b + arr[v1 + 4])
    if v2 >= 4:
        a = u32(a + (arr[v1 + 3] << 24))
    if v2 >= 3:
        a = u32(a + (arr[v1 + 2] << 16))
    if v2 >= 2:
        a = u32(a + (arr[v1 + 1] << 8))
    if v2 >= 1:
        a = u32(a + arr[v1])

    return mix32_2(a, b, c)


# ================= HELPERS =================

def hex_be(v): return f"0x{v:08X}"
def hex_le(v): return f"0x{int.from_bytes(v.to_bytes(4,'little'),'big'):08X}"

def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def load_custom_font(font_filename):
    font_path = os.path.join(app_dir(), font_filename)
    if os.path.exists(font_path):
        ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)

# ================= UI =================
customtkinter.deactivate_automatic_dpi_awareness()
load_custom_font("RobotoMono.ttf")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("NFS-Hasher v3.0")
root.geometry("525x370")
root.resizable(False, False)

# Set native window icon
icon_path = os.path.join(app_dir(), "NFS.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

FONT_LABEL = ("Roboto Mono", 17, "bold")
FONT_INPUT = ("Roboto Mono", 16, "bold")
FONT_FIELD = ("Roboto Mono", 16)
FIELD_TEXT_COLOR = "#7A7A7A"
FIELD_HIGHLIGHT_COLOR = "#D09900"  # copied highlight (orange)
FIELD_BORDER_COLOR = "#484848"

def center_window(root):
    root.update_idletasks()

    width = root.winfo_width()
    height = root.winfo_height()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root.geometry(f"{width}x{height}+{x}+{y}")


frame = ctk.CTkFrame(root, fg_color="transparent")
frame.pack(fill="both", expand=True, padx=16, pady=12)

status_copied = ctk.CTkLabel(
    root,
    text="",
    font=("Roboto Mono", 16, "bold"),
    text_color="#D09900"   # gold
)
status_copied.place(relx=0.45, y=350, anchor="e")
status_rest = ctk.CTkLabel(
    root,
    text="",
    font=("Roboto Mono", 16, "bold"),
    text_color="#FFFFFF"   # white
)
status_rest.place(relx=0.45, y=350, anchor="w")

def show_copied():
    status_copied.configure(text="Copied ")
    status_rest.configure(text="to clipboard")

    root.after(1000, clear_status)

def clear_status():
    status_copied.configure(text="")
    status_rest.configure(text="")

def bind_copy(entry, var):
    entry.bind("<Button-1>", lambda e: (
        root.clipboard_clear(),
        root.clipboard_append(var.get()),
        root.update(),
        show_copied()
    ))
    entry.bind("<Key>", lambda _: "break")

def field(row, col, var, width=200, text_color=FIELD_TEXT_COLOR):
    e = ctk.CTkEntry(
        frame,
        textvariable=var,
        font=FONT_FIELD,
        width=width,
        text_color=text_color,
        border_color=FIELD_BORDER_COLOR
    )
    e.grid(row=row, column=col, sticky="w", padx=8, pady=6)

    def on_click(_):
        value = var.get()
        if not value:
            return

        # Copy to clipboard
        root.clipboard_clear()
        root.clipboard_append(value)
        root.update()

        # Highlight this field only
        e.configure(text_color=FIELD_HIGHLIGHT_COLOR)

        # Bottom animation
        show_copied()

        # Restore color after animation
        root.after(1000, lambda: e.configure(text_color=text_color))

    # Click-to-copy + animation
    e.bind("<Button-1>", on_click)

    # Read-only but selectable
    e.bind("<Key>", lambda _: "break")

    return e


# ================= VARIABLES =================

input_var = tk.StringVar()

bin_mem = tk.StringVar()
bin_mem_dec = tk.StringVar()
bin_file = tk.StringVar()
bin_file_dec = tk.StringVar()
bin_mem_hex = tk.StringVar()
bin_file_hex = tk.StringVar()
vlt_mem_hex = tk.StringVar()
vlt_file_hex = tk.StringVar()
vlt_mem = tk.StringVar()
vlt_mem_dec = tk.StringVar()
vlt_file = tk.StringVar()
vlt_file_dec = tk.StringVar()

def clear_all():
    for v in [
        bin_mem, bin_mem_hex, bin_mem_dec,
        bin_file, bin_file_hex, bin_file_dec,
        vlt_mem, vlt_mem_hex, vlt_mem_dec,
        vlt_file, vlt_file_hex, vlt_file_dec
    ]:
        v.set("")

def update_hash(*_):
    text = input_var.get()
    if not text:
        clear_all()
        return

    # ---------- BIN ----------
    bh = bin_hash_prefix(text)

    bin_mem.set(hex_le(bh))
    bin_file.set(hex_be(bh))

    bin_mem_hex.set(bin_mem.get().removeprefix("0x"))
    bin_file_hex.set(bin_file.get().removeprefix("0x"))

    bin_mem_dec.set(str(int(bin_mem_hex.get(), 16)))
    bin_file_dec.set(str(int(bin_file_hex.get(), 16)))

    # ---------- VLT (RAW, OGVI-compatible) ----------
    vh_dec = vlt_hash_32(text)           # DECIMAL (Raider)
    vh_hex = f"0x{vh_dec:08X}"           # HEX display (OGVI / Binarius)

    # File = big endian (canonical VLT hash)
    vlt_file.set(vh_hex)

    # Memory = little endian view
    vlt_mem.set(hex_le(vh_dec))

    # HEX (no 0x)
    vlt_file_hex.set(vh_hex[2:])
    vlt_mem_hex.set(vlt_mem.get().removeprefix("0x"))

    # DEC
    vlt_file_dec.set(str(vh_dec))
    vlt_mem_dec.set(str(int(vlt_mem_hex.get(), 16)))

input_var.trace_add("write", update_hash)


def h_separator(row, col_span=4, pady=(10, 10)):
    sep = ctk.CTkFrame(
        frame,
        height=2,
        fg_color=("#1a1a1a", "#1a1a1a")  # subtle dark line
    )
    sep.grid(
        row=row,
        column=0,
        columnspan=col_span,
        sticky="ew",
        pady=pady
    )
# ================= LAYOUT =================

# INPUT
ctk.CTkLabel(frame, text="INPUT", font=FONT_LABEL, text_color="#D09900").grid(row=0, column=0, sticky="w")
ctk.CTkEntry(
    frame, textvariable=input_var, font=FONT_INPUT, width=417, text_color="#D09900", border_color="#484848").grid(row=0, column=1, columnspan=3, padx=8, pady=8)

# ---- separator between INPUT and BIN
h_separator(row=1)

# BIN headers
ctk.CTkLabel(frame, text="BIN", font=FONT_LABEL, text_color="#D09900")\
    .grid(row=2, column=0, sticky="w")

ctk.CTkLabel(frame, text="HEX", font=FONT_LABEL, text_color="#7A7A7A")\
    .grid(row=2, column=1, sticky="w", padx=(10, 0))

ctk.CTkLabel(frame, text="DEC", font=FONT_LABEL, text_color="#7A7A7A")\
    .grid(row=2, column=2, sticky="w", padx=(10, 0))

# BIN memory
ctk.CTkLabel(frame, text="Memory", font=FONT_FIELD)\
    .grid(row=3, column=0, sticky="w", padx=(0, 10))

field(3, 1, bin_file_hex)
field(3, 2, bin_file_dec)

# BIN file
ctk.CTkLabel(frame, text="File", font=FONT_FIELD)\
    .grid(row=4, column=0, sticky="w", padx=(0, 10))

field(4, 1, bin_mem_hex)
field(4, 2, bin_mem_dec)

# ---- separator between BIN and VLT
h_separator(row=5, pady=(14, 14))

# VLT headers
ctk.CTkLabel(frame, text="VLT", font=FONT_LABEL, text_color="#D09900")\
    .grid(row=6, column=0, sticky="w")

ctk.CTkLabel(frame, text="HEX", font=FONT_LABEL, text_color="#7A7A7A")\
    .grid(row=6, column=1, sticky="w", padx=(10, 0))

ctk.CTkLabel(frame, text="DEC", font=FONT_LABEL, text_color="#7A7A7A")\
    .grid(row=6, column=2, sticky="w", padx=(10, 0))

# VLT memory
ctk.CTkLabel(frame, text="Memory", font=FONT_FIELD)\
    .grid(row=7, column=0, sticky="w", padx=(0, 10))


field(7, 1, vlt_file_hex)
field(7, 2, vlt_file_dec)

# VLT file
ctk.CTkLabel(frame, text="File", font=FONT_FIELD)\
    .grid(row=8, column=0, sticky="w", padx=(0, 10))


field(8, 1, vlt_mem_hex)
field(8, 2, vlt_mem_dec)



root.after(0, lambda: center_window(root))
root.mainloop()