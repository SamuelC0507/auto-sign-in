import os
from datetime import datetime

tag_executable = 2  # 0: No; 1: Release; 2: Debug
file_name = "log_analyzer.py"
title_origin = "Log Analyzer"
title_tmp = ""
tag = "Debug"


def add_tag():
    global title_tmp, tag

    with open(file_name) as f:
        s = f.read()

    with open(file_name, 'w') as f:
        start_idx = s.find("window.title(\"" + title_origin)
        end_idx = s.find("\")", start_idx)
        title_tmp = s[start_idx:end_idx + 2]
        if tag_executable == 1:
            tag = datetime.now().strftime("%y%m%d")
        s = s.replace(title_tmp, "window.title(\"" + title_origin + " " + tag + "\")")
        f.write(s)


def remove_tag():
    with open(file_name) as f:
        s = f.read()

    with open(file_name, 'w') as f:
        s = s.replace("window.title(\"" + title_origin + " " + tag + "\")", title_tmp)
        f.write(s)


if tag_executable != 0:
    add_tag()

os.popen("pyinstaller --clean -y -w -F -n " + title_origin.replace(" ", "") + " " + file_name).read()

if tag_executable > 1:
    remove_tag()

os.popen("rmdir /s /q .\\build").read()
os.popen("del /q " + file_name.split(".")[0] + ".spec").read()
