"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM, gethostname, gethostbyname
import requests
from threading import Thread
import ScreenShareGUI as SShareGUI
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
                msg_area.insert(tkinter.END, msg+"\n")
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
    global top

    # when window is close send a quit message to the server as well
    my_msg.set("{quit}")
    try:
        send()
    finally:
        print(2)
        top.quit()
        print("top.quit() passed")
        raise KeyboardInterrupt


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
    wrap=tkinter.WORD
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

chars = [n for n in "',<>;:[]{}()-_+=`~!@#$%^&*\\|"+'"'+"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"]

#----Now comes the sockets part----
HOST = input('Enter host: ')
PORT = input('Enter port: ')
if not PORT:
    PORT = 5050
else:
    PORT = int(PORT)

HOST = [HOST.replace(n, "") for n in chars][-1]

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive, daemon=True)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.