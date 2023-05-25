# importing some sick libraries
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import *
import pygame
from io import BytesIO
from PIL import ImageTk, Image
import requests
from pytube import YouTube, Playlist
import threading
import re
from random import randint

# making main window. some settings here
root = tk.Tk()
root.geometry('600x400')
root.iconbitmap('haroldownloader.ico')
root.resizable(False, False)
root.title("HarolDownloader")
background = "haroldback.png"

# i dont know why its here
url = tk.StringVar()
pygame.mixer.init()


# some lists which store (pl_urls = store urls from playlist) (itag = store tag to download)
pl_urls = []
itag = []

#store if the link is single or playlsit
single = True

def load():
    global single
    global itag

    play()
    link = url.get().strip()
    single = "list=" not in link

    #checking url correctivness
    if not check_url(link):
        alert("Incorrect URL", "Please write correct url")
        return
    
    listboxer.delete(0, tk.END)
    
    if single:   
        try: 
            #youtube
            yt = YouTube(link)
            #sorting all possible youtube videos
            video_audio = yt.streams.filter(progressive=True)[::-1]
            video = yt.streams.filter(only_video=True)
            audio = yt.streams.filter(only_audio=True)
            chanima(yt)
        except:
            alert("Error", "Dude something went wrong (ur fault)")
            return

        itag.clear()
        listboxer.config(selectmode="normal")
        listboxer.delete(0, tk.END)

        #showing all items in listbox and appending their itag to list
        for i in video_audio:
            ext = i.mime_type.split("/")[1]
            itag.append(i.itag)
            listboxer.insert(tk.END, f"{i.resolution} {i.fps}fps {ext} with audio")
        for i in video:
            ext = i.mime_type.split("/")[1]
            itag.append(i.itag)
            listboxer.insert(tk.END, f"{i.resolution} {i.fps}fps {ext}")
        for i in audio:
            ext = i.mime_type.split("/")[1]
            if ext == "mp4":
                ext = "mp3"
            itag.append(i.itag)
            listboxer.insert(tk.END, f"audio {i.abr} {ext}")
    else:
        # displaying titles to choose and storing the video urls
        global pl_urls
        try:
            pl = Playlist(link)
            chanima(pl.videos[0])
        except:
            alert("Error", "Dude something went wrong (ur fault)")
            return
        listboxer.config(selectmode="multiple")
        for video in pl.videos:
            listboxer.insert(tk.END, video.title)
        pl_urls = pl.video_urls


chosen = False
def download():
    global pl_urls
    global chosen
    global itag
    play()
    if chosen:
        thread = threading.Thread(target=downanim)
        thread.start()
        select = listboxer.curselection()[0]
        tag = itag[int(select)]
        foldername = filedialog.askdirectory()
        if foldername == "":
            return
        for vid in pl_urls:
            yt = YouTube(vid)
            exten = "." + listboxer.get(tk.ANCHOR).split(" ")[2]
            stream = yt.streams.get_by_itag(tag)
            stream.download(output_path=foldername, filename=clean_title(yt.title) + exten)
        return
    if single:
        thread = threading.Thread(target=downanim)
        thread.start()
        foldername = filedialog.askdirectory()
        if foldername == "":
            return
        # ~0.2% rick easter egg ;)
        r = randint(0, 420)
        link = "https://youtu.be/dQw4w9WgXcQ" if r == 69 else url.get().strip()
        yt = YouTube(link)
        select = listboxer.curselection()[0]
        tag = itag[int(select)]
        exten = "." + listboxer.get(tk.ANCHOR).split(" ")[2]
        stream = yt.streams.get_by_itag(tag)
        stream.download(output_path=foldername, filename=clean_title(yt.title) + exten)
    else:
        listboxer.config(selectmode="normal")
        pl_urls = [pl_urls[i] for i in listboxer.curselection()]
        # you have to make one change to cipher.py in pytube for more than 3 videos to work
        # https://stackoverflow.com/questions/70776558/pytube-exceptions-regexmatcherror-init-could-not-find-match-for-w-w
        ytbs = [YouTube(u) for u in pl_urls]
        ytbs_streams = [[str(j) for j in i.streams] for i in ytbs]
        ytbs_streams = list(set.intersection(*map(set, ytbs_streams)))
        listboxer.delete(0, tk.END)
        itag.clear()
        for i in ytbs_streams:
            # res fps format audio?
            if changer(i, "type").split("/")[0] == "video":
                res = changer(i, "res")
                fps = changer(i, "fps")
                ext = changer(i, "mime_type").split("/")[1]
                is_audio = "with audio" if changer(i, "progressive") == "True" else ""
                string = f"{res} {fps} {ext} {is_audio}"
                listboxer.insert(tk.END, string)
            else:
                abr = changer(i, "abr")
                ext = changer(i, "mime_type").split("/")[1]
                string = f"audio {abr} {ext}"
                listboxer.insert(tk.END, string)
            itag.append(changer(i, "itag"))
        chosen = True



def check_url(link):
    u = requests.get(f"https://www.youtube.com/oembed?format=json&url={link}")
    if u.status_code != 200:
        return False
    return True

def clear_url():
    play()
    e.delete(0, 'end')

def changer(text, s):
    pattern = r'{0}="([^"]*)"'.format(s)
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return None

def clean_title(title):
    word = ["/", "\\", ":", "\"", "*", "?", "<", ">", "|", "."]
    title = "".join(list(filter(lambda i: not i in word, title.split("|")[0])))
    return title

def downanim():
    import anim

# some cool staff here to make the app more powerfull
def alert(title, message, kind='warning'):
    if kind == "warning":
        pygame.mixer.music.load('harold_error_clicker.mp3')
        pygame.mixer.music.play(loops=0)
    show_method = getattr(messagebox, 'show{}'.format(kind))
    show_method(title, message)

def play():
    # yes we use pygame because tkinter not support changing audio :DDDD
    pygame.mixer.music.load('harold_clicker.mp3')
    pygame.mixer.music.play(loops=0)

def chanima(yt):
    u = requests.get(yt.thumbnail_url)
    img = ImageTk.PhotoImage(Image.open(BytesIO(u.content)).resize((600, 400)))
    label.configure(image=img)
    label.image = img

#some sick fonts here
Font = ("Cambria", 14)
Fonts = ("Cambria", 9, "bold")

#set background
backimg = tk.PhotoImage(file=background)
label = tk.Label(root, image=backimg)
label.place(x=0, y=0)

#btn that clear text
btn_clear = tk.Button(root, text="x", bg="#ff2021",
                 activebackground="#ff2021", fg="#FFFFFF", command=clear_url, width=2, font=Fonts)
btn_clear.pack(side='right', anchor='ne')

#entry that get from user url
e = tk.Entry(root, textvariable=url, width=69, font=Font)
e.pack()

#button to load data from url
btn_load = tk.Button(root, text="load", bg="#ff2021",
                activebackground="#ff2021", fg="#FFFFFF", command=load, font=Font)
btn_load.pack()

#load data into listbox
listboxer = tk.Listbox(root, width=70, font=Fonts)
listboxer.pack()

#btn to download choosen video
btn_download = tk.Button(root, text="download", bg="#ff2021",
                 activebackground="#ff2021", fg="#FFFFFF", command=download, font=Font)
btn_download.pack()

root.mainloop()