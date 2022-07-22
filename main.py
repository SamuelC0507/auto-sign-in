import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import time
import threading
import numpy as np
import cv2
import mss
import mss.tools
from pynput import mouse, keyboard
import re
import json
import requests
import webbrowser
from selenium import webdriver
import pytesseract


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
    global roi_flag

    roi_flag = 0
    url_history.clear()
    btn_select_roi.config(state=tk.DISABLED, relief=tk.SUNKEN)
    print_log("Waiting for ROI selection...")
    listener = mouse.Listener(on_click=on_click)
    listener.start()


def cancel_roi():
    global roi_flag

    roi_flag = 0


def show_roi():
    global roi_flag

    print_log("Start monitoring ROI")
    sct = mss.mss()
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    url = ""
    step = 0
    roi_flag = 1
    btn_cancel_roi.config(state=tk.NORMAL)
    while True:
        sct_img = np.array(sct.grab(bounding_box))
        cv2.imshow('ROI', sct_img)

        cv2.waitKey(1)  # (cv2.waitKey(1) & 0xFF) == ord('q')
        if roi_flag == 0:
            cv2.destroyAllWindows()
            print_log("Monitoring ended")
            btn_cancel_roi.config(state=tk.DISABLED)
            break

        image_text = pytesseract.image_to_string(sct_img)
        url_start_idx = image_text.lower().find("http")
        if url_start_idx != -1:
            url = image_text[url_start_idx:image_text[url_start_idx:].find("\n\n")].replace("\n", "").replace(" ", "")
            if url.lower() in url_history:
                continue

            if cbt_prompt_val.get() and step == 0:
                tk.messagebox.askokcancel('Warning', 'Taking control of mouse and keyboard')

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
            # fixed_tabbing()
            # selenium_driver()
            entry_id()


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


def selenium_driver():
    kb.press(keyboard.Key.f6)
    kb.release(keyboard.Key.f6)
    time.sleep(1)
    with kb.pressed(keyboard.Key.ctrl):
        kb.press("c")
        kb.release("c")
        kb.press("w")
        kb.release("w")

    options = webdriver.ChromeOptions()
    if cbt_profile_val.get():
        options.add_argument("user-data-dir=" + profile_path)
    options.add_argument("incognito")
    options.add_argument("disable-web-security")
    options.add_argument("allow-running-insecure-content")
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    driver.get(tk.Tk().clipboard_get())
    time.sleep(1)

    textboxes = driver.find_elements_by_class_name("quantumWizTextinputPaperinputInput")
    radiobuttons = driver.find_elements_by_class_name("docssharedWizToggleLabeledLabelWrapper")
    if len(textboxes) != 2 or len(radiobuttons) != 0:
        print_log("This is not a roll call form")
    else:
        textboxes[0].send_keys(ent_id_val.get())
        textboxes[1].send_keys(ent_name_val.get())
        submit = driver.find_element_by_xpath('//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div/div/span/span')
        submit.click()

    time.sleep(3)
    driver.quit()


def entry_id():
    kb.press(keyboard.Key.f6)
    kb.release(keyboard.Key.f6)
    time.sleep(1)
    with kb.pressed(keyboard.Key.ctrl):
        kb.press("c")
        kb.release("c")
        kb.press("w")
        kb.release("w")

    url = tk.Tk().clipboard_get()

    if url.find(r"://docs.google.com/forms/") == -1:
        print_log("This is not a Google Form")
        return

    html_data = requests.get(url).text
    data = json.loads(re.search(r'FB_PUBLIC_LOAD_DATA_ = (.*?);', html_data, flags=re.S).group(1))
    data_list = []
    for i in data[1][1]:
        if len(i) == 5:
            if i[4][0][1] is None:
                if i[1] == "學號":
                    data_list.append([i[1], i[4][0][0], ent_id_val.get()])
                elif i[1] == "姓名":
                    data_list.append([i[1], i[4][0][0], ent_name_val.get()])
                else:
                    data_list.append([i[1], i[4][0][0], "No idea"])
            else:
                data_list.append([i[1], i[4][0][0], i[4][0][1][0][0]])

    for i in range(len(data_list)):
        if "學號" in data_list[i]:
            if len(data_list) == 2:
                print_log("Roll call form")
            else:
                print_log("Quiz form")
            break
        if i == len(data_list) - 1:
            print_log("Unknown form")

    ans_str = ""
    for i in data_list:
        ans_str += "entry." + str(i[1]) + "=" + str(i[2]) + "&"
    url_to_be_submitted = url.replace("viewform", "formResponse?" + ans_str)
    webbrowser.open(url_to_be_submitted)

    time.sleep(3)
    with kb.pressed(keyboard.Key.ctrl):
        kb.press("w")
        kb.release("w")


def select_tesseract():
    global tesseract_path

    filepath = filedialog.askopenfilename(initialdir=".\\", filetypes=[("EXE Files", ".exe")])
    if not filepath:
        return

    tesseract_path = filepath
    if len(tesseract_path) > lbl_tesseract["width"]:
        lbl_tesseract.configure(text="..." + tesseract_path[-lbl_tesseract["width"] + 3:])
    else:
        lbl_tesseract.configure(text=tesseract_path)


def select_chromedriver():
    global chromedriver_path

    filepath = filedialog.askopenfilename(initialdir=".\\", filetypes=[("EXE Files", ".exe")])
    if not filepath:
        return

    chromedriver_path = filepath
    if len(chromedriver_path) > lbl_chromedriver["width"]:
        lbl_chromedriver.configure(text="..." + chromedriver_path[-lbl_chromedriver["width"] + 3:])
    else:
        lbl_chromedriver.configure(text=chromedriver_path)


def select_profile():
    global profile_path

    filepath = filedialog.askdirectory(initialdir=".\\", mustexist=True)
    if not filepath:
        return

    profile_path = filepath
    if len(profile_path) > lbl_profile["width"]:
        lbl_profile.configure(text="..." + profile_path[-lbl_profile["width"] + 3:])
    else:
        lbl_profile.configure(text=profile_path)


def enable_profile(trace_a, trace_b, trace_c):
    if cbt_profile_val.get():
        btn_select_profile.configure(state=tk.NORMAL)
        lbl_profile.configure(state=tk.NORMAL)
    else:
        btn_select_profile.configure(state=tk.DISABLED)
        lbl_profile.configure(state=tk.DISABLED)


def print_log(msg):
    if int(txt_log.index('end-1c').split('.')[0]) > 100:
        txt_log.delete("1.0", "2.0")
    txt_log.insert(tk.END, time.strftime("%X") + " - " + msg + "\n")
    txt_log.see(tk.END)


def on_closing():
    window.destroy()


# Global
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
chromedriver_path = r"C:\Sam\Program_Files\chromedriver_win32\chromedriver.exe"
profile_path = r"C:\Users\oldch\AppData\Local\Google\Chrome\User Data"
bounding_box = {'left': 0, 'top': 0, 'width': 0, 'height': 0}
url_history = []
ms = mouse.Controller()
kb = keyboard.Controller()
roi_flag = 0

# GUI window
window = tk.Tk()
window.title("Auto Sign In")
window.minsize(800, 400)
window.protocol("WM_DELETE_WINDOW", on_closing)

# Frame frm_roi
frm_roi = tk.Frame()
frm_roi.pack(anchor="w", padx=10, pady=(10, 0))
btn_select_roi = tk.Button(master=frm_roi, text="Select ROI", width=8, command=select_roi)
btn_select_roi.pack(side=tk.LEFT)
btn_cancel_roi = tk.Button(master=frm_roi, text="Cancel ROI", width=8, command=cancel_roi, state=tk.DISABLED)
btn_cancel_roi.pack(side=tk.LEFT, padx=(10, 0))
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
cbt_prompt_val = tk.IntVar()
cbt_prompt = tk.Checkbutton(master=frm_roi, text="Prompt Verification", variable=cbt_prompt_val)
cbt_prompt.pack(side=tk.LEFT, padx=(10, 0))

# Frame frm_tesseract
frm_tesseract = tk.Frame()
frm_tesseract.pack(anchor="w", padx=10, pady=(10, 0))
btn_select_tesseract = tk.Button(master=frm_tesseract, text="Select Tesseract", width=12, command=select_tesseract)
btn_select_tesseract.pack(side=tk.LEFT)
lbl_tesseract = tk.Label(master=frm_tesseract, text=tesseract_path, anchor=tk.SW, width=80)
lbl_tesseract.pack(side=tk.LEFT)

# Frame frm_chromedriver
frm_chromedriver = tk.Frame()
# frm_chromedriver.pack(anchor="w", padx=10, pady=(10, 0))
btn_select_chromedriver = tk.Button(master=frm_chromedriver, text="Select ChromeDriver", width=16, command=select_chromedriver)
btn_select_chromedriver.pack(side=tk.LEFT)
lbl_chromedriver = tk.Label(master=frm_chromedriver, anchor=tk.SW, width=34)
if len(chromedriver_path) > lbl_chromedriver["width"]:
    lbl_chromedriver.configure(text="..." + chromedriver_path[-lbl_chromedriver["width"] + 3:])
else:
    lbl_chromedriver.configure(text=chromedriver_path)
lbl_chromedriver.pack(side=tk.LEFT)
cbt_profile_val = tk.IntVar()
cbt_profile_val.trace('w', enable_profile)
cbt_profile = tk.Checkbutton(master=frm_chromedriver, text="Use Profile", variable=cbt_profile_val)
cbt_profile.pack(side=tk.LEFT)
btn_select_profile = tk.Button(master=frm_chromedriver, text="Select Profile", width=12, command=select_profile)
btn_select_profile.pack(side=tk.LEFT)
lbl_profile = tk.Label(master=frm_chromedriver, anchor=tk.SW, width=34)
if len(profile_path) > lbl_profile["width"]:
    lbl_profile.configure(text="..." + profile_path[-lbl_profile["width"] + 3:])
else:
    lbl_profile.configure(text=profile_path)
lbl_profile.pack(side=tk.LEFT)
cbt_profile_val.set(0)

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
