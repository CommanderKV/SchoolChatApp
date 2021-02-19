"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread

clients = {}
reciveing_screenshares = {}
sending_screenshares = {}
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
        client.send(bytes("[MSG] Welcome! Now type your username and press enter!", "utf8"))

        reciveing_screenshare = f"[SCREENSHARE_{client_address[0]}_R]"
        sending_screenshare = f"[SCREENSHARE_{client_address[0]}_S]"

        # get the username from the user and send out a welcome message if
        # the user is not a screenshare account 
        username = client.recv(BUFSIZ).decode("utf8")
        if username != reciveing_screenshare and username != sending_screenshare:

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


def handle_sending_screenshare(client):
    pass


def handle_reciveing_screenshare(client):
    pass


def handle_client(client, username):  # Takes client socket as argument.
    """Handles a single client connection."""

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

