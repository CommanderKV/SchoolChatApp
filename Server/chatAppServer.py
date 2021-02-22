"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread
import pygame


clients = {}
reciveing_screenshares = {}
sending_screenshares = {}
screenshares = {}
addresses = {}

HOST = "0.0.0.0"
PORT = 5050
BUFSIZ = 1024
ADDR = (HOST, PORT)
print(f"Connect to IP: {gethostbyname(gethostname())}, PORT: {PORT}")

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()

        # display who connected at what ip and port
        print(f"{client_address[0]}:{client_address[1]} has connected.")

        # send welcome message to get username
        client.send(bytes("[MSG] Welcome! Now type your username and press enter!", "utf8"))

        reciveing_screenshare = f"[SCREENSHARE_{client_address[0]}_R]"
        sending_screenshare = f"[SCREENSHARE_{client_address[0]}_S]"
        amount_screenshare = f"[SCREENSHARE_{client_address[0]}_A]"

        ScreenShareUsernames = [
            reciveing_screenshare,
            sending_screenshare,
            amount_screenshare
        ]

        # get the username from the user and send out a welcome message if
        # the user is not a screenshare account 
        username = client.recv(BUFSIZ).decode("utf8")
        print(username)
        if username not in ScreenShareUsernames:

            # send welcome message
            welcome = f"[MSG] Welcome {username}! If you ever want to quit, type '"+"{quit}"+"' to exit."
            client.send(bytes(welcome, "utf8"))

            # add this user to a dictonary
            addresses[client] = client_address

            # start a individual thread for this client
            Thread(target=handle_client, args=(client, username)).start()
        
        # if the account is a screenshare account
        elif username == reciveing_screenshare:

            # save the screenshare acoount
            reciveing_screenshare[client] = client_address

            # start a thread to handle reciving screenshare accounts
            Thread(target=handle_reciveing_screenshare, args=(client,)).start()

        # if the account is a sending screenshare account
        elif username == sending_screenshare:
            
            # save the screenshare account
            sending_screenshares[client] = client_address

            # start a thread to handle sending screenshare accounts
            Thread(target=handle_sending_screenshare, args=(client,)).start()
        
        # if the account is requesting the amount of screens give it to them
        elif username == amount_screenshare:

            # get the amount of current screenshares
            amount = bytes(str(len(screenshares)), "utf-8")

            # send back the requested data
            client.sendall(amount)


def handle_sending_screenshare(client):
    """Handling each sending ScreenShare account"""
    # client is a socket conection

    def convertPixels(reciver, length):
        "Retrives all pixels"

        buf = b""
        while len(buf) < length:
            data = reciver.recv(length-len(buf))
            if not data:
                return data
            buf += data
        return buf

    run = True
    while run:
        # running or not?
        continueTF = True if client.recv(1024).decode("utf-8") == "True" else False
        if continueTF == False:
            run = False
            break

        # get the size of the image
        imsize = (int.from_bytes(client.recv(1024)), int.from_bytes(client.recv(1024)))

        # get data on the image
        size_len = int.from_bytes(client.recv(1), byteorder="big")
        size = int.from_bytes(client.recv(size_len), byteorder="big")
        pixels = convertPixels(client, size)

        #          Username of their already 
        #              signed in account, pixels, size,  type
        screenshares[clients[client]] = [pixels, imsize, "RGB"]
    
    del screenshares[clients[client]]
    del sending_screenshares[client]


def handle_reciveing_screenshare(client):
    """Handles all of the reciving conections"""
    # client is a socket conection
    msg = client.recv(1024)
    allOrNone = True if msg.decode("utf-8") == "ALL" else int.from_bytes(msg)

    run = True
    while run:
        # running or not?
        continueTF = True if client.recv(1024).decode("utf-8") == "True" else False
        if continueTF == False:
            run = False
            break
        
        if allOrNone == True:
            for username in screenshares:
                
                # send the username
                client.sendall(bytes(str(username), "utf-8"))

                # send the pixels
                client.sendall(screenshares[username][0])

                # send the image size
                client.sendall(bytes(str(screenshares[username][1][0]), "utf-8"))
                client.sendall(bytes(str(screenshares[username][1][1]), "utf-8"))

                # send the type of image
                client.sendall(bytes(screenshares[username][2], "utf-8"))
                
        else:
            # get the username
            username = screenshares[allOrNone]

            # send the username
            client.sendall(bytes(str(username), "utf-8"))

            # send the pixels
            client.sendall(screenshares[username][0])

            # send the image size
            client.sendall(bytes(str(screenshares[username][1][0]), "utf-8"))
            client.sendall(bytes(str(screenshares[username][1][1]), "utf-8"))

            # send the type of image
            client.sendall(bytes(screenshares[username][2], "utf-8"))

    

def handle_client(client, username):  # Takes client socket as argument.
    """Handles a single client connection."""

    # tell everyone that the user joined the chat
    msg = f"{username} has joined the chat!"
    print(len(clients))
    broadcast(bytes(msg, "utf8"))

    # add the user to the clients list
    clients[client] = username

    while True:
        # recive a message
        msg = client.recv(BUFSIZ)

        # if the message is not quit then send msg
        if msg != bytes("{quit}", "utf8") or msg != bytes("{serverQuit}", "utf8"):
            try:
                broadcast(msg, username+": ")
            except:
                client.close()
                del clients[client]
                quit()
        
        # if the message is for the server to shutdown
        elif msg == bytes("{serverQuit}", "utf8"):
            client.close()
            del clients[client]
            quit()

        # if the message is quit then
        else:
            # close the client conection
            client.send(bytes("[MSG] {quit}", "utf8"))
            client.close()
            del clients[client]

            # tell everyone that they have left
            broadcast(bytes(f"{username} has left the chat.", "utf8"))

            # close their client down
            break


def broadcast(msg, prefix="", msgTF=True):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    # add the send note "[MSG] " to prefix before sending
    # this is used to tell if it is a message or a diffrent data type
    if msgTF == True:
        prefix = "[MSG] " + prefix

    # sends a message to all users
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()

