# importing some sick libraries
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import *
import pygame
from io import BytesIO
from PIL import ImageTk, Image
import requests
from pytube import YouTube, Playlist
import re
from random import randint

# making main window. some settings here
root = ctk.CTk()
root.geometry('600x400')
root.iconphoto(False, tk.PhotoImage(file='haroldownloader.png'))
root.resizable(False, False)
root.title("HarolDownloader")
background = "haroldback.png"

colors = {
    "green-dark": "#005c00",
    "green-dark+": "#004b00",
    "green-bright": "#0ecd0e",
    "yellow": "#f2f230",
    "bg": "#282828",
    "text": "#ffffff"
}

# i dont know why its here
url = tk.StringVar()
pygame.mixer.init()


# some lists which store (pl_urls = store urls from playlist) (itag = store tag to download)
pl_urls = []
itag = []

link = ""

# store if the link is single or playlsit
single = True

chosen = False

def clear_url(_):
    play()
    e.delete(0, 'end')

def play():
    # yes we use pygame because tkinter not support changing audio :DDDD
    pygame.mixer.music.load('harold_clicker.mp3')
    pygame.mixer.music.play(loops=0)


def back():
    global backimg
    play()
    f_search.pack(expand=True, anchor="center", padx=25)
    btn_backtosearch.place_forget()
    listboxer.pack_forget()
    f_d.pack_forget()
    label.configure(image=backimg)
    label.image = backimg


def enter(event):
    if event.keysym == 'Return':
        search()

def search():
    global link, single, itag
    play()
    link = url.get().strip()
    if not check_url(link):
        alert("Incorrect URL", "Please write correct url")
        return
    if "open.spotify.com" in link:
        link = get_yt_url(link)
        single = True
    else:
        single = "list=" not in link
    listboxer.delete(0, tk.END)
    f_search.pack_forget()
    btn_backtosearch.place(x=20, y=20)
    listboxer.pack(pady=80)
    f_d.pack()
    if single:
        btn_download.pack()
        try:
            yt = YouTube(link)
            # sorting all possible youtube videos
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

        # showing all items in listbox and appending their itag to list
        for i in video_audio:
            ext = i.mime_type.split("/")[1]
            itag.append(i.itag)
            listboxer.insert(
                tk.END, f"{i.resolution} {i.fps}fps {ext} with audio")
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
        btn_dall.pack(side='right')
        btn_download.pack()
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
    


def check_url(link):
    return requests.get(f"https://www.youtube.com/oembed?url={link}").status_code == 200 or requests.get(f"https://open.spotify.com/oembed?url={link}").status_code == 200

def download(oll: bool = False):
    global pl_urls
    global chosen
    global itag
    global link
    play()
    if chosen:
        select = listboxer.curselection()[0]
        tag = itag[int(select)]
        foldername = filedialog.askdirectory()
        if foldername == "":
            return
        for vid in pl_urls:
            yt = YouTube(vid)
            exten = "." + listboxer.get(tk.ANCHOR).split(" ")[2]
            stream = yt.streams.get_by_itag(tag)
            stream.download(output_path=foldername,
                            filename=clean_title(yt.title) + exten)
        alert("Succes", "Download complete. Take coffe and relax", kind="info")
        return
    if single:
        select = listboxer.curselection()[0]
        tag = itag[int(select)]
        foldername = filedialog.askdirectory()
        if foldername == "":
            return
        # ~0.2% rick easter egg ;)
        r = randint(0, 420)
        link = "https://youtu.be/dQw4w9WgXcQ" if r == 69 else link
        yt = YouTube(link)
        exten = "." + listboxer.get(tk.ANCHOR).split(" ")[2]
        stream = yt.streams.get_by_itag(tag)
        stream.download(output_path=foldername,
                        filename=clean_title(yt.title) + exten)
        alert("Succes", "Download complete. Take coffe and relax", kind="info")
    else:
        listboxer.config(selectmode="normal")
        pl_urls = [pl_urls[i]
                   for i in listboxer.curselection()] if not oll else pl_urls
        # you have to make one change to cipher.py in pytube for more than 3 videos to work
        # https://stackoverflow.com/questions/70776558/pytube-exceptions-regexmatcherror-init-could-not-find-match-for-w-w
        # https://stackoverflow.com/questions/68945080/pytube-exceptions-regexmatcherror-get-throttling-function-name-could-not-find
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
                is_audio = "with audio" if changer(
                    i, "progressive") == "True" else ""
                string = f"{res} {fps} {ext} {is_audio}"
                listboxer.insert(tk.END, string)
            else:
                abr = changer(i, "abr")
                ext = changer(i, "mime_type").split("/")[1]
                string = f"audio {abr} {ext}"
                listboxer.insert(tk.END, string)
            itag.append(changer(i, "itag"))
        chosen = True
        btn_dall.place_forget()


def chanima(yt):
    u = requests.get(yt.thumbnail_url)
    img = ImageTk.PhotoImage(Image.open(BytesIO(u.content)).resize((600, 400)))
    label.configure(image=img)
    label.image = img

def alert(title, message, kind='warning'):
    if kind == "warning":
        pygame.mixer.music.load('harold_error_clicker.mp3')
        pygame.mixer.music.play(loops=0)
    show_method = getattr(messagebox, 'show{}'.format(kind))
    show_method(title, message)



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

def get_yt_url(url):
    response = requests.get(url)
    i = str(response.content).find("<title>")
    j = str(response.content).find("</title>")
    title = str(response.content)[i+7:j]
    response = requests.get(f'https://www.youtube.com/results?search_query={title}')
    k = str(response.content).find("/watch?v=")
    print(("https://www.youtube.com/watch?v="+str(response.content)[k+9:k+20]))
    return("https://www.youtube.com/watch?v="+str(response.content)[k+9:k+20])



def dall():
    download(True)



# some sick fonts here
Font = ("caladea", 16)
Fonts = ("caladea", 9, "bold")

# set background
backimg = tk.PhotoImage(file=background)
label = tk.Label(root, image=backimg)
label.place(x=0, y=0)


f_search = tk.Frame(root)
f_search.pack(expand=True, anchor="center", padx=25)

Style().configure('TButton', background=colors["green-dark"], activebackground=colors["green-bright"], foreground=colors["yellow"], font=Font)
Style().map('TButton',background=[('active', colors["green-dark+"])])

btn_search = Button(f_search, width=3, text="🔍", command=search)
btn_search.pack(side='right', anchor='ne', ipady=2)

Style().configure('TEntry', borderwidth=0,  insertcolor=colors["text"], fieldbackground=colors["bg"], foreground=colors["text"])

f_eb = tk.Frame(f_search, background=colors["bg"])
f_eb.pack()

btn_clear = Label(f_eb, width=2, text="x", anchor="center", background=colors["bg"], foreground=colors["yellow"], font=Font)
btn_clear.pack(side='right', anchor='center')

e = Entry(f_eb, textvariable=url, width=50, justify="center", font=Font)
e.pack(ipady=6, ipadx=20)
e.focus()

listboxer = tk.Listbox(root, width=70, font=Fonts, background=colors["bg"], bd=0, highlightthickness=0, foreground=colors["text"])

f_d = tk.Frame(root)

btn_download = Button(f_d, text="Download", command=download)
btn_dall = Button(f_d, text="all", command=dall, width=3)

btn_backtosearch = Button(root, width=3, text="🔙", command=back)

btn_clear.bind("<Button-1>", clear_url)
e.bind("<Key>", enter)


root.mainloop()