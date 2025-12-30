import json
import subprocess
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import shutil
import os
import requests

with open("credentials.json", "r", encoding="utf-8") as f:
    creds = json.load(f)

username = creds["username"]
password = creds["password"]

url = "https://raw.githubusercontent.com/Instel12/Baldi-s-Basics-Plus-Downgrader/main/manifest.json"

try:
    response = requests.get(url)
    response.raise_for_status()  # Raises an error if request failed
    manifests = response.json()
except requests.exceptions.RequestException as e:
    messagebox.showerror("Error", f"Failed to fetch manifest.json:\n{e}")
    manifests = {}

# Keep the order from JSON instead of sorting
manifests_items = manifests.items()

ROOT_DIR = Path(__file__).parent
DEPOTS_DIR = ROOT_DIR / "depots" / "1275891" / "21271401"
VERSIONS_DIR = ROOT_DIR / "versions"
VERSIONS_DIR.mkdir(exist_ok=True)

def is_downloaded(version_name):
    return (VERSIONS_DIR / version_name).exists()

def handle_version(version_name, manifest_id, button):
    version_path = VERSIONS_DIR / version_name
    baldi_exe = version_path / "BALDI.exe"

    if baldi_exe.exists():
        try:
            os.startfile(baldi_exe)
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch BALDI.exe:\n{e}")
    else:
        # Run DepotDownloader
        cmd = [
            "./DepotDownloader.exe",
            "-username", username,
            "-password", password,
            "-app", "1275890",
            "-depot", "1275891",
            "-manifest", str(manifest_id)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                messagebox.showerror("Download Error", f"Failed to download manifest {manifest_id}:\n{result.stderr}")
                return
            
            if DEPOTS_DIR.exists():
                shutil.move(str(DEPOTS_DIR), str(version_path))
                messagebox.showinfo("Download Complete", f"Version {version_name} downloaded successfully!")
                if button:
                    button.config(text="Open")
            else:
                messagebox.showerror("Error", f"Expected folder {DEPOTS_DIR} not found after download.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("BBP Downgrader")
root.geometry("500x600")
root.resizable(False, False)

icon_image = tk.PhotoImage(file=str(ROOT_DIR / "icon.png"))
root.iconphoto(True, icon_image)

canvas = tk.Canvas(root, borderwidth=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=500)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def resize_canvas(event):
    canvas.itemconfig(canvas_window, width=event.width)

canvas.bind("<Configure>", resize_canvas)

# Iterate over manifests_items without sorting
for i, (version, info) in enumerate(manifests_items):
    manifest_id = info["manifest"]
    bg_color = "#f0f0f0" if i % 2 == 0 else "#ffffff"

    row_frame = tk.Frame(scrollable_frame, bg=bg_color)
    row_frame.pack(fill="x", pady=1)

    label = tk.Label(row_frame, text=version, bg=bg_color)
    label.pack(side="left", padx=(10, 0))

    btn_text = "Open" if is_downloaded(version) else "Download"
    btn = tk.Button(
        row_frame,
        text=btn_text,
        width=10,
        command=lambda v=version, m=manifest_id, b=None: handle_version(v, m, b),
    )
    btn.config(command=lambda v=version, m=manifest_id, b=btn: handle_version(v, m, b))
    btn.pack(side="right", padx=(0, 10))

def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", on_mousewheel)

root.mainloop()
