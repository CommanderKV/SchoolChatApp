"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread

clients = {}
addresses = {}

HOST = "0.0.0.0"
PORT = 80
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
        client.send(bytes("Welcome! Now type your username and press enter!", "utf8"))

        # add this user to a dictonary
        addresses[client] = client_address

        # start a individual thread for this client
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    # get the username from the user and send out a welcome message
    username = client.recv(BUFSIZ).decode("utf8")
    welcome = f"Welcome {username}! If you ever want to quit, type '"+"{quit}"+"' to exit."
    client.send(bytes(welcome, "utf8"))

    # tell everyone that the user joined the chat
    msg = f"{username} has joined the chat!"
    broadcast(bytes(msg, "utf8"))

    # add the user to the clients list
    clients[client] = username

    while True:
        # recive a message
        msg = client.recv(BUFSIZ)

        # if the message is not quit then send msg
        if msg != bytes("{quit}", "utf8") or msg != bytes("{serverQuit}", "utf8"):
            broadcast(msg, username+": ")
        
        # if the message is for the server to shutdown
        elif msg == bytes("{serverQuit}", "utf8"):
            client.close()
            del clients[client]
            quit()

        # if the message is quit then
        else:
            # close the client conection
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]

            # tell everyone that they have left
            broadcast(bytes(f"{username} has left the chat.", "utf8"))

            # close their client down
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

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


"""
import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 65432
BUFFER = 1024

def server():
    global IP, PORT

    # makeing a users dictonary
    users = {}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((IP, PORT))
        server.listen()
        connected, ip = server.accept()
        
        recivedData = connected.recv(BUFFER)
        recivedData = str(repr(recivedData)).replace("b'", "").replace("'", "")

        users[recivedData] = ip

        with connected:
            print(f"{recivedData} conected to the server at: (ip: {ip[0]}, port: {ip[0]})")

            run = True
            i = 0
            while run:
                recivedData = connected.recv(BUFFER)
                if str(recivedData) != "b''":
                    recivedData = str(repr(recivedData)).replace("b'", "").replace("'", "")
                    if recivedData != "HEARTBEAT":
                        print(f"{recivedData}")

                        # if our input is SERVER EXIT then it will close the server down
                        if recivedData == "SERVER EXIT":
                            run = False
                            print("Exiting Program")
                        i += 1
                        connected.sendall(bytes(str(i), "utf-8"))
                    
                    # this is a heartbeat response back to the server
                    else:
                        print("[NOTE] 'HEARTBEAT' recived")
                        i = 0


def client():
    global IP, PORT

    # connect to the ip and port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((IP, PORT))
        client.sendall(bytes(str(input("What is your username?\nMy username is: ")), "utf-8"))
        spacing = 28
        
        run = True
        while run:
            # add some line spacing
            print("\n"*spacing)

            # makeing sure it is a vaild input
            sendMeOri = str(input("You: "))+"*//*"
            while sendMeOri == "*//*":
                print("\n"*spacing)
                print("[ERROR] input not recognized")
                sendMeOri = str(input("You: "))+"*//*"

            sendMeOri = sendMeOri.replace("*//*", "")

            # send the message
            sendMe = bytes(sendMeOri, "utf-8")
            client.sendall(sendMe)

            # if the message is EXIT then end the program
            if sendMeOri == "EXIT":
                run = False

            # check to see if heartbeat needs to be sent
            recivedData = client.recv(BUFFER)
            if str(recivedData) != "b''":
                    recivedData = str(repr(recivedData)).replace("b'", "").replace("'", "")
                    if int(recivedData) == 10:
                        client.sendall(b"HEARTBEAT")

chat = input("Do you want to chat?\nY/N: ")

if chat == "N":
    server()
elif chat == "Y":
    client()

"""
