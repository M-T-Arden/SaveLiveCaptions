import sys
import os
import asyncio
import tkinter as tk
from tkinter import filedialog
import time
import aiofiles

file_handle = None 
saved_captions = set()
save_dir = ""

def choose_save_dir():
    global save_dir
    
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())  

    if not save_dir:
        root = tk.Tk()
        root.withdraw()  
        save_dir = filedialog.askdirectory(
            title="choose direction",
            initialdir=os.path.expanduser("~")  
        )
        root.destroy()  

        if not save_dir:
            save_dir = os.path.expanduser("~/Documents/captions")
            os.makedirs(save_dir, exist_ok=True)
    
    filename = os.path.join(save_dir, f"{timestamp}_captions.txt")
    
    return filename

async def save_txt(filename, caption):
    global file_handle
       
    if file_handle is None:
        file_handle = await aiofiles.open(filename, "a+", encoding="utf-8")
    
    crt_time = time.time()
    crt_time_formatted = time.strftime("%H:%M:%S", time.localtime(crt_time))
    
    if caption not in saved_captions:
        await file_handle.write(f"[{crt_time_formatted}] {caption}\n")
        await file_handle.flush()
        saved_captions.add(caption)
    
async def close_file():
    global file_handle
    if file_handle is not None:
        await file_handle.close()
        file_handle = None