"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM, gethostname, gethostbyname
import requests
from threading import Thread
import ScreenShareGUI as SShareGUI
from functools import partial
import HeartBeat
import tkinter
import time
import sys


def receive():
    """Handles receiving of messages."""
    
    # attempts to recive a message
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if "[MSG] " in msg:
                
                msg = msg.replace("[MSG] ", "")
                msg_area.configure(state="normal")
                msg_area.insert(tkinter.END, msg+"\n")
                msg_area.configure(state="disabled")
                msg_area.yview(tkinter.END)

            elif msg == "{quit}":
                client_socket.close()
                top.quit()
                break
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    # get the text in the tkinter input
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.

    # send the message to the server
    client_socket.send(bytes(msg, "utf8"))
    # if message is to quit then quit
    if msg == "{quit}":
        client_socket.close()
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    global top, STOP_HEARTBEAT

    # when window is close send a quit message to the server as well
    my_msg.set("{quit}")
    try:
        send()
    finally:
        STOP_HEARTBEAT = True
        top.quit()


def reset(event=None):
    """Resets the input boxs text to nothing if the text is the same as the startng text."""
    # if the text is the same as the starting text
    if my_msg.get() == "Type your messages here.":
        my_msg.set("") # clear the entry_field


def openMenu():
    global ADDR
    SShareGUI.Main(ADDR)


def openScreenShareMenu(event=None):
    Thread(target=openMenu, daemon=True).start()


def openNewWindow(): 
    global newWindow
    def setHostPort(host, port, newWindow):
        host = host.get()
        port = int(port.get())
        startClient(host, port)
      
    # Toplevel object which will  
    # be treated as a new window 
    newWindow = tkinter.Toplevel(top) 
  
    # sets the title of the 
    # Toplevel widget 
    newWindow.title("Login") 
  
    # sets the geometry of toplevel 
    newWindow.geometry("205x67") 
    
    #username label and text entry box
    hostLabel = tkinter.Label(newWindow, text="Host").grid(row=0, column=0)
    host = tkinter.StringVar()
    hostEntry = tkinter.Entry(newWindow, textvariable=host).grid(row=0, column=1)

    #password label and password entry box
    portLabel = tkinter.Label(newWindow,text="Port").grid(row=1, column=0)
    port = tkinter.StringVar()
    portEntry = tkinter.Entry(newWindow, textvariable=port).grid(row=1, column=1)

    setTheHostAndPort = partial(setHostPort, host, port, newWindow)

    login = tkinter.Button(newWindow, text="Login", command=setTheHostAndPort).grid(row=2, column=0)


def startClient(host, port):
    global HOST, PORT, BUFSIZ, ADDR, STOP_HEARTBEAT, client_socket

    HOST = host
    PORT = port
    chars = [n for n in "',<>;:[]{}()-_+=`~!@#$%^&*\\|"+'"'+"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"]

    if not PORT:
        PORT = 5050
    else:
        PORT = int(PORT)

    HOST = [HOST.replace(n, "") for n in chars][-1]

    BUFSIZ = 1024
    ADDR = (HOST, PORT)

    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.settimeout(2.0)
        client_socket.connect(ADDR)
        client_socket.settimeout(10)

        receive_thread = Thread(target=receive, daemon=True)
        receive_thread.start()

        STOP_HEARTBEAT = False

        heartBeat_Thread = Thread(target=HeartBeat.main, args=(ADDR, lambda: STOP_HEARTBEAT,), daemon=True)
        heartBeat_Thread.start()
    except:
        print("Invaild input")
        return
    
    newWindow.destroy()
    top.focus_force()


top = tkinter.Tk()
top.title("School Chat")

# setting up the message box and its scrollbar
messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Type your messages here.")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.

# Following will contain the messages.
msg_area = tkinter.Text(
    messages_frame, 
    height=25, 
    width=83, 
    yscrollcommand=scrollbar.set, 
    font=("comicsans", 10), 
    wrap=tkinter.WORD,
    state="disabled"
)


scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_area.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_area.pack()
messages_frame.pack()

# making the entry field for input from users
text_input_size = 60
text_font = ("Comicsans", 10)

# make and add text input to the window
entry_field = tkinter.Entry(top, textvariable=my_msg, width=text_input_size, font=text_font)
entry_field.bind("<Return>", send)
entry_field.bind("<Button-1>", reset)
entry_field.pack(side=tkinter.LEFT, padx=10, pady=20, ipady=5)

# make and add a screen share button
screenshare = tkinter.Button(top, text="Screenshare", command=openScreenShareMenu, bg="white")
screenshare.pack(side=tkinter.RIGHT, padx=10)

# make and add a send button to the window
send_button = tkinter.Button(top, text="Send", command=send, bg="white")
send_button.pack(side=tkinter.RIGHT, padx=20, pady=20)

top.protocol("WM_DELETE_WINDOW", on_closing)

openNewWindow()
newWindow.attributes("-topmost", True)
top.attributes("-topmost", False)
tkinter.mainloop()  # Starts GUI execution.

