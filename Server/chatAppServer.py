"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread
from zlib import decompress


clients = {}
reciveing_screenshares = {}
sending_screenshares = {}
screenshares = {}
usernames = {}
addresses = {}

HOST = "0.0.0.0"
PORT = 5050
BUFSIZ = 1024
ADDR = (HOST, PORT)
print(f"Connect to IP: {gethostbyname(gethostname())}, PORT: {PORT}")

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    global reciveing_screenshares, sending_screenshares, screenshares
    global clients, addresses

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
            Thread(target=handle_client, args=(client, username, client_address[0],), daemon=True).start()
        
        # if the account is a screenshare account
        elif username == reciveing_screenshare:

            # save the screenshare acoount
            reciveing_screenshare[client] = client_address

            # start a thread to handle reciving screenshare accounts
            Thread(target=handle_reciveing_screenshare, args=(client,), daemon=True).start()

        # if the account is a sending screenshare account
        elif username == sending_screenshare:
            
            # save the screenshare account
            sending_screenshares[client] = client_address

            # start a thread to handle sending screenshare accounts
            Thread(target=handle_sending_screenshare, args=(client, client_address[0],), daemon=True).start()
        
        # if the account is requesting the amount of screens give it to them
        elif username == amount_screenshare:

            # get the amount of current screenshares
            length_screenshares = len(screenshares)
            amount = length_screenshares.to_bytes(((length_screenshares.bit_length()+7)//8), byteorder="big")

            # send back the requested data
            client.sendall(amount)


def convertPixels(reciver, length):
    """Retrives all pixels"""

    buf = b""
    while len(buf) < length:
        data = reciver.recv(length-len(buf))
        if not data:
            return data
        buf += data
    return buf


def handle_sending_screenshare(client, hostname):
    """Handling each sending ScreenShare account"""
    # client is a socket conection
    global screenshares
    global clients
    global sending_screenshares

    try:
        run = True
        while run:
            # running or not?
            msgSize = int.from_bytes(client.recv(1), byteorder="big")
            #print(f"msgSize: '{msgSize}'")

            msg = client.recv(msgSize).decode("utf-8")
            #print(f"msg: '{msg}'")

            continueTF = True if msg == "True" else False
            if continueTF == False:
                run = False
                break
                

            # get the size of the image
            imsize1Len = int.from_bytes(client.recv(1), byteorder="big")
            imsize1 = int.from_bytes(client.recv(imsize1Len), byteorder="big")
            imsize1 *= 100

            imsize2Len = int.from_bytes(client.recv(1), byteorder="big")
            imsize2 = int.from_bytes(client.recv(imsize2Len), byteorder="big")
            imsize2 *= 100

            imsize = (
                imsize1, 
                imsize2
            )
            #print(f"imsize: '{imsize}'")

            # get data on the image
            size_len = int.from_bytes(client.recv(1), byteorder="big")
            #print(f"size_len: '{size_len}'")

            size = int.from_bytes(client.recv(size_len), byteorder="big")
            #print(f"size: '{size}'")

            pixels = decompress(convertPixels(client, size))
            #print(f"pixels len: '{len(pixels)}'")

            #          Username of their already 
            #              signed in account,    pixels, size,  type
            screenshares[usernames[hostname]] = [pixels, imsize, "RGB"]
    
    except:
        run = False
        client.close()

        for name in screenshares:
            if name == usernames[hostname]:
                print(f"Selecting this to delete: '{name}'")
            else:
                print(name)

        del screenshares[usernames[hostname]]
        del sending_screenshares[client]


def handle_reciveing_screenshare(client):
    """Handles all of the reciving conections"""
    #    dict\/      str\/    str?\/ tupple\/  str\/
    # screenshares[username] = [pixels, imsize, "RGB"]

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


def handle_client(client, username, hostname):  # Takes client socket as argument.
    """Handles a single client connection."""
    global clients

    # tell everyone that the user joined the chat
    msg = f"{username} has joined the chat!"
    print(f"Amount of pepole conected: {len(clients)+1}")
    broadcast(bytes(msg, "utf8"))

    # add the user to the clients list
    clients[client] = username
    usernames[hostname] = username

    while True:
        # recive a message  
        try:
            msg = client.recv(BUFSIZ)
        except:
            msg = None

        if msg != None:
            # if the message is not quit then send msg
            if msg != bytes("{quit}", "utf8") or msg != bytes("{serverQuit}", "utf8"):
                try:
                    broadcast(msg, username+": ")
                except:
                    client.close()
                    del clients[client]
                    break
            
            # if the message is for the server to shutdown
            elif msg == bytes("{serverQuit}", "utf8"):
                client.close()
                for AClient in clients:
                    AClient.close()
                    del clients[AClient]
                break
                

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
    print(f"Amount of pepole conected: {len(clients)}")


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
    ACCEPT_THREAD = Thread(target=accept_incoming_connections, daemon=True)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()

