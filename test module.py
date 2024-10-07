import os
import pyautogui as pg
import time
a = "dude"
txtpath = "C:\\ProgramFiles\\Google\\Chrome\\Application\chrome.exe."
os.startfile(txtpath)
time.sleep(2)

pg.hotkey('ctrl','a')
pg.hotkey('ctrl','c')
pg.click(300,980)
time.sleep(2)
b =  input(pg.hotkey(button = "right"))
print(b)
if a in b:
    print("Its working dude")




