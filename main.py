import tkinter as tk
import time
import threading
import numpy as np
import cv2
import mss
import mss.tools
from pynput import mouse
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\\Sam\\Program_Files\\Tesseract-OCR\\tesseract.exe"
# pytesseract.pytesseract.tesseract_cmd = "D:\\Sam\\Program_files\\Tesseract-OCR\\tesseract.exe"


def on_click(x, y, button, pressed):
    global bounding_box

    if button.name == "right":
        if pressed:
            bounding_box["left"] = x
            bounding_box["top"] = y
        else:
            bounding_box["width"] = abs(x - bounding_box["left"])
            bounding_box["left"] = min(bounding_box["left"], x)
            bounding_box["height"] = abs(y - bounding_box["top"])
            bounding_box["top"] = min(bounding_box["top"], y)

            btn_select_roi.config(state=tk.NORMAL, relief=tk.RAISED)
            print_log("ROI: " + str(list(bounding_box.values())))

            show_roi_thread = threading.Thread(target=show_roi, daemon=True)
            show_roi_thread.start()
            return False


def select_roi():
    btn_select_roi.config(state=tk.DISABLED, relief=tk.SUNKEN)
    print_log("Waiting for ROI selection...")
    listener = mouse.Listener(on_click=on_click)
    listener.start()


def show_roi():
    sct = mss.mss()
    ms = mouse.Controller()
    step = 0
    while True:
        sct_img = np.array(sct.grab(bounding_box))
        cv2.imshow('ROI', sct_img)

        image_text = pytesseract.image_to_string(sct_img)
        url_start_idx = image_text.find("https")
        if url_start_idx != -1:
            url = image_text[url_start_idx:image_text.find("viewform") + 8].replace("\n", "").replace(" ", "")
            print("URL detected: " + url)

            ms.position = (bounding_box["left"] + int(bounding_box["width"] / 3), bounding_box["top"] + step)
            ms.click(mouse.Button.left, 1)
            step += 10
        else:
            step = 0

        if (cv2.waitKey(1) & 0xFF) == ord('q') or btn_select_roi["state"] == tk.DISABLED:
            cv2.destroyAllWindows()
            break


def print_log(msg):
    if int(txt_log.index('end-1c').split('.')[0]) > 100:
        txt_log.delete("1.0", "2.0")
    txt_log.insert(tk.END, time.strftime("%X") + " - " + msg + "\n")
    txt_log.see(tk.END)


def on_closing():
    window.destroy()


# Global
bounding_box = {'left': 0, 'top': 0, 'width': 0, 'height': 0}

# GUI window
window = tk.Tk()
window.title("Auto Sign In")
window.minsize(400, 300)
window.protocol("WM_DELETE_WINDOW", on_closing)

# Frame frm_roi
frm_roi = tk.Frame()
frm_roi.pack(anchor="w", padx=10, pady=(10, 0))
btn_select_roi = tk.Button(master=frm_roi, text="Select ROI", width=10, command=select_roi)
btn_select_roi.pack(side=tk.LEFT)

# Frame frm_log
frm_log = tk.Frame()
frm_log.pack(anchor="w", padx=10, pady=(10, 10), expand=True, fill=tk.BOTH)
txt_log = tk.Text(master=frm_log, wrap=tk.WORD, width=10, height=10)
txt_log.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
txt_log.bind("<Key>", lambda e: "break")
scb_log = tk.Scrollbar(master=frm_log, command=txt_log.yview)
scb_log.pack(side=tk.LEFT, fill=tk.Y)
txt_log.configure(yscrollcommand=scb_log.set)

print_log("Program launched successfully")

window.mainloop()
