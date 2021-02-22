"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM, gethostname, gethostbyname
import requests
from threading import Thread
import ScreenShareGUI as SShareGUI
import tkinter


def receive():
    """Handles receiving of messages."""
    
    # attempts to recive a message
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if "[MSG] " in msg:
                msg_list.insert(tkinter.END, msg.replace("[MSG] ", ""))
                msg_list.see("end")
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    # get the text in the tkinter input
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.

    # send the message to the server
    client_socket.send(bytes(msg, "utf8"))
    print(0)
    # if message is to quit then quit
    if msg == "{quit}":
        client_socket.close()
        print(1)
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""

    # when window is close send a quit message to the server as well
    my_msg.set("{quit}")
    send()
    print(2)
    quit()


def reset(event=None):
    """Resets the input boxs text to nothing if the text is the same as the startng text."""
    # if the text is the same as the starting text
    if my_msg.get() == "Type your messages here.":
        my_msg.set("") # clear the entry_field


def startScreenShareMenu():
    SShareGUI.Main(ADDR)

def openScreenShareMenu(event=None):
    Thread(target=startScreenShareMenu).start()

top = tkinter.Tk()
top.title("School Chat")

# setting up the message box and its scrollbar
messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Type your messages here.")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=25, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
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

#----Now comes the sockets part----
HOST = input('Enter host: ')
PORT = input('Enter port: ')
if not PORT:
    PORT = 80
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.