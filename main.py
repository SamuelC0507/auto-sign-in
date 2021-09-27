import tkinter as tk
import time
import numpy as np
import cv2
import mss
import mss.tools
import webbrowser
import pyautogui
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\\Sam\\Program_Files\\Tesseract-OCR\\tesseract.exe"


def select_roi():
    sct = mss.mss()
    monitor_number = 2
    mon = sct.monitors[monitor_number]
    bounding_box = {'top': mon["top"] + 1600, 'left': mon["left"] + 3200, 'width': 600, 'height': 200, 'mon': monitor_number}

    while True:
        sct_img = np.array(sct.grab(bounding_box))
        cv2.imshow('ROI', sct_img)

        # sct_img = cv2.resize(sct_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        # kernel = np.ones((2, 2), np.uint8)
        # sct_img = cv2.dilate(sct_img, kernel, iterations=1)
        # sct_img = cv2.erode(sct_img, kernel, iterations=1)
        # sct_img = cv2.cvtColor(sct_img, cv2.COLOR_BGR2GRAY)
        # sct_img = cv2.threshold(sct_img, 160, 255, cv2.THRESH_BINARY)[1]
        # cv2.imshow('ROI2', sct_img)

        image_text = pytesseract.image_to_string(sct_img, config='--psm 6')
        # print(image_text)
        url_start_idx = image_text.find("https")
        if url_start_idx != -1:
            url = image_text[url_start_idx:image_text.find("viewform") + 8].replace("\n", "").replace(" ", "")
            print("URL detected: " + url)
            # webbrowser.open(url)

            pyautogui.click(bounding_box["left"] + int(bounding_box["width"] / 2), bounding_box["top"])

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break


def print_log(msg):
    if int(txt_log.index('end-1c').split('.')[0]) > 100:
        txt_log.delete("1.0", "2.0")
    txt_log.insert(tk.END, time.strftime("%X") + " - " + msg + "\n")
    txt_log.see(tk.END)


def on_closing():
    window.destroy()


# GUI window
window = tk.Tk()
window.title("Auto Sign In")
window.minsize(400, 300)
window.protocol("WM_DELETE_WINDOW", on_closing)

# Frame frm_roi
frm_roi = tk.Frame()
frm_roi.pack(anchor="w", padx=10, pady=(10, 0))
btn_play = tk.Button(master=frm_roi, text="Select ROI", width=10, command=select_roi)
btn_play.pack(side=tk.LEFT)

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
