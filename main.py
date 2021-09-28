import tkinter as tk
import time
import threading
import numpy as np
import cv2
import mss
import mss.tools
from pynput import mouse, keyboard
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
    url = ""
    step = 0
    while True:
        sct_img = np.array(sct.grab(bounding_box))
        cv2.imshow('ROI', sct_img)

        if (cv2.waitKey(1) & 0xFF) == ord('q') or btn_select_roi["state"] == tk.DISABLED:
            cv2.destroyAllWindows()
            break

        image_text = pytesseract.image_to_string(sct_img)
        url_start_idx = image_text.lower().find("https")
        if url_start_idx != -1:
            url = image_text[url_start_idx:image_text[url_start_idx:].find("\n\n")].replace("\n", "").replace(" ", "")
            if url.lower() in url_history:
                continue

            ms.position = (bounding_box["left"] + int(bounding_box["width"] / 3), bounding_box["top"] + step)
            ms.click(mouse.Button.left, 1)
            step += 10
            if step >= bounding_box["height"]:
                print_log("Invalid URL: " + url)
                url_history.append(url.lower())
                if len(url_history) > 3:
                    url_history.pop(0)
                step = 0
        elif step != 0:
            print_log("URL: " + url)
            url_history.append(url.lower())
            if len(url_history) > 3:
                url_history.pop(0)
            step = 0

            time.sleep(3)
            fixed_tabbing()


def fixed_tabbing():
    kb.press(keyboard.Key.tab)
    kb.release(keyboard.Key.tab)
    kb.press(keyboard.Key.tab)
    kb.release(keyboard.Key.tab)
    kb.press(keyboard.Key.tab)
    kb.release(keyboard.Key.tab)
    kb.type(ent_id_val.get())
    kb.press(keyboard.Key.tab)
    kb.release(keyboard.Key.tab)
    kb.type(ent_name_val.get())
    kb.press(keyboard.Key.tab)
    kb.release(keyboard.Key.tab)
    kb.press(keyboard.Key.enter)
    kb.release(keyboard.Key.enter)
    time.sleep(3)

    with kb.pressed(keyboard.Key.ctrl):
        kb.press("w")
        kb.release("w")


def print_log(msg):
    if int(txt_log.index('end-1c').split('.')[0]) > 100:
        txt_log.delete("1.0", "2.0")
    txt_log.insert(tk.END, time.strftime("%X") + " - " + msg + "\n")
    txt_log.see(tk.END)


def on_closing():
    window.destroy()


# Global
bounding_box = {'left': 0, 'top': 0, 'width': 0, 'height': 0}
url_history = []
ms = mouse.Controller()
kb = keyboard.Controller()

# GUI window
window = tk.Tk()
window.title("Auto Sign In")
window.minsize(800, 400)
window.protocol("WM_DELETE_WINDOW", on_closing)

# Frame frm_roi
frm_roi = tk.Frame()
frm_roi.pack(anchor="w", padx=10, pady=(10, 0))
btn_select_roi = tk.Button(master=frm_roi, text="Select ROI", width=10, command=select_roi)
btn_select_roi.pack(side=tk.LEFT)
lbl_id = tk.Label(master=frm_roi, text="ID:")
lbl_id.pack(side=tk.LEFT, padx=(10, 0))
ent_id_val = tk.StringVar(value="B0229050")
ent_id = tk.Entry(master=frm_roi, width=20, textvariable=ent_id_val)
ent_id.pack(side=tk.LEFT)
lbl_name = tk.Label(master=frm_roi, text="Name:")
lbl_name.pack(side=tk.LEFT, padx=(10, 0))
ent_name_val = tk.StringVar(value="Samuel Chang")
ent_name = tk.Entry(master=frm_roi, width=20, textvariable=ent_name_val)
ent_name.pack(side=tk.LEFT)

# Frame frm_log
frm_log = tk.Frame()
frm_log.pack(anchor="w", padx=10, pady=(10, 10), expand=True, fill=tk.BOTH)
txt_log = tk.Text(master=frm_log, wrap=tk.WORD, width=10, height=10, font="Consolas 8")
txt_log.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
txt_log.bind("<Key>", lambda e: "break")
scb_log = tk.Scrollbar(master=frm_log, command=txt_log.yview)
scb_log.pack(side=tk.LEFT, fill=tk.Y)
txt_log.configure(yscrollcommand=scb_log.set)

print_log("Program launched successfully")

window.mainloop()
