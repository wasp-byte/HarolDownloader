import tkinter as tk
from tkinter.ttk import *
import time
import random

w = tk.Tk()
w.overrideredirect(1)
w.attributes("-topmost", True)
width_of_window = 427
height_of_window = 250
screen_width = w.winfo_screenwidth()
screen_height = w.winfo_screenheight()
x_coordinate = (screen_width/2)-(width_of_window/2)
y_coordinate = (screen_height/2)-(height_of_window/2)
w.geometry("%dx%d+%d+%d" %(width_of_window,height_of_window,x_coordinate,y_coordinate))


s = Style()
s.theme_use('clam')
s.configure("red.Horizontal.TProgressbar", foreground='red', background='red')
progress=Progressbar(w,style="red.Horizontal.TProgressbar",orient=tk.HORIZONTAL,length=500,mode='determinate')
progress.place(x=-10,y=235)

def bar():
    r=0
    for i in range(100):
        progress['value']=r
        w.update_idletasks()
        time.sleep(0.1)
        r=r+1
    w.destroy()
img = tk.PhotoImage(file=f"background{random.randint(1, 3)}.png", master=w)
label = tk.Label(
    w,width=427, height=238,
    image=img
)
label.place(x=0, y=0)

w.after(1000, bar)
w.mainloop()