"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM, gethostbyname, gethostname, timeout
import time
from threading import Thread
from zlib import decompress
import HeartBeat


clients = {}
clients_HeartBeats = {}
reciveing_screenshares = {}
sending_screenshares = {}
screenshares = {}
usernames = {}
addresses = {}
hostnames = []
nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

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
        try:
            SERVER.settimeout(1.0)
            client, client_address = SERVER.accept()
        except timeout:
            continue

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

        # set the hostname for this account
        hostname = client_address[0].replace(".", "")
        total = 0
        for number in hostname:
            total += int(number)
            
        hostname = total

        while hostname in hostnames:
            hostname += 1

        # get the username from the user and send out a welcome message if
        # the user is not a screenshare account
        
        try:
            username = client.recv(BUFSIZ).decode("utf8")
        except:
            client.close()
            continue

        print(f"Username used to login: {username}")
        if username not in ScreenShareUsernames:

            # add a 1 to the end of the username if the username is already signed in
            for c in clients:
                if clients[c] == username:
                    temp = username[-1:]
                    if temp in nums:
                        temp = str(int(temp)+1)
                    else:
                        username = str(username)+"0"

            # send welcome message
            pings = 0
            try:
                welcome = f"[MSG] Welcome {username}! If you ever want to quit, type '"+"{quit}"+"' to exit."
                client.send(bytes(welcome, "utf8"))

            except:
                pings += 1
                sent = False
                print(f"[PING] Sent '{pings}/10' pings to: '{client_address[0]}:{client_address[1]}' with no response")
                
                while sent == False and pings != 10:
                    try:
                        welcome = f"[MSG] Welcome {username}! If you ever want to quit, type '"+"{quit}"+"' to exit."
                        client.send(bytes(welcome, "utf8"))
                        sent = True

                    except:
                        pings += 1
                        print(f"[PING] Sent '{pings}/10' pings to: '{client_address[0]}:{client_address[1]}' with no response")
                
                if pings == 10:
                    print(f"[CONNECTION-ERROR] Sent '{pings}/10' pings to: '{client_address[0]}:{client_address[1]}' with no success")
                    print(f"[CONNECTION-ERROR] Abandoning attepmt to connect to: '{client_address[0]}:{client_address[1]}'")
                    continue


            # add this user to a dictonary
            addresses[client] = client_address

            # start a individual thread for this client
            name = f"'{client_address[0]}:{client_address[1]}'-Client-Thread"
            Thread(
                name=name,
                target=handle_client, 
                args=(
                    client, 
                    username, 
                    hostname, 
                    client_address,
                ), 
                daemon=True
            ).start()
        
        # if the account is a screenshare account
        elif username == reciveing_screenshare:

            # save the screenshare acoount
            reciveing_screenshares[client] = client_address

            # start a thread to handle reciving screenshare accounts
            name = f"'{client_address[0]}:{client_address[1]}'-RecvScreenShare-Thread"
            Thread(
                name=name,
                target=handle_reciveing_screenshare, 
                args=(
                    client,
                ), 
                daemon=True
            ).start()

        # if the account is a sending screenshare account
        elif username == sending_screenshare:
            
            # save the screenshare account
            sending_screenshares[client] = client_address

            # start a thread to handle sending screenshare accounts
            name = f"'{client_address[0]}:{client_address[1]}'-SendScreenShare-Thread"
            Thread(
                name=name,
                target=handle_sending_screenshare, 
                args=(
                    client, 
                    hostname,
                ), 
                daemon=True
            ).start()
        
        # if the account is requesting the amount of screens give it to them
        elif username == amount_screenshare:

            # get the amount of current screenshares
            length_screenshares1 = len(screenshares)
            length_screenshares = length_screenshares1.to_bytes(
                ((length_screenshares1.bit_length()+7)//8), 
                byteorder="big"
            )

            len_Length_screenshares = ((length_screenshares1.bit_length()+7)//8)
            len_Length_screenshares = len_Length_screenshares.to_bytes(
                ((len_Length_screenshares.bit_length()+7)//8),
                byteorder="big"
            )

            # send the length of the amount
            client.sendall(len_Length_screenshares)

            # send back the requested data
            client.sendall(length_screenshares)
            
            # close the client
            client.close()


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
    hostname -= 1
    hostname = str(hostname)

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

            pixels = convertPixels(client, size)
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

    # get the size of all or a num
    size = int.from_bytes(client.recv(1), byteorder="big")

    # get all or a num
    msg = client.recv(size)
    allOrNone = True if msg.decode("utf-8") == "ALL" else int.from_bytes(msg, byteorder="big")
    msg_str = msg.decode("utf-8")
    msg_int = int.from_bytes(msg, byteorder="big")
    print(f"Recived: '{msg_str} or {msg_int}'")

    run = True
    while run:
        # running or not?
        conn = client.recv(1024).decode("utf-8")
        continueTF = True if conn == "True" else False
        print(f"Recived: '{conn}'")
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
            username = [n for n in screenshares][allOrNone-1]

            # send the username
            client.sendall(bytes(str(username), "utf-8"))
            print(f"Sending: '{username}'")

            # send the length of pixels length
            pixels_len = len(screenshares[username][0])
            pixels_length_len = ((pixels_len.bit_length()+7)//8)
            pixels_length_len = pixels_length_len.to_bytes(
                ((pixels_length_len.bit_length()+7)//8), 
                byteorder="big"
            )
            client.sendall(pixels_length_len)
            print(f"Sending: '{len(pixels_len)}, {pixels_length_len}'")

            # send the pixels length
            pixels_len = pixels_len.to_bytes(
                ((pixels_len.bit_length()+7)//8),
                byteorder="big"
            )
            client.sendall(pixels_len)
            print(f"Sending: '{len(screenshares[username][0])}, {pixels_len}'")

            # send the pixels
            client.sendall(screenshares[username][0])
            print(f"Sending: '{str(screenshares[username][0])[:10]}...'")

            # send the image size
            imsize = screenshares[username][1][0]//100
            client.sendall(imsize.to_bytes(
                    ((imsize.bit_length()+7)//8), 
                    byteorder="big"
                )
            )
            print(f"Sending: '{screenshares[username][1][0]}'")

            imsize = screenshares[username][1][1]//100
            client.sendall(imsize.to_bytes(
                    ((imsize.bit_length()+7)//8), 
                    byteorder="big"
                )
            )
            print(f"Sending: '{screenshares[username][1][1]}'")

            # send the type of image
            client.sendall(bytes(screenshares[username][2], "utf-8"))
            print(f"Sending: '{screenshares[username][2]}'")


def handle_client(client, username, hostname, client_addr):  # Takes client socket as argument.
    """Handles a single client connection."""
    global clients, usernames, clients_HeartBeats, checkpulsexit, hostnames

    hostname = str(hostname)
    hostnames.append(hostname)

    # add the user to the clients list
    clients[client] = username
    usernames[hostname] = username
    checkpulsexit = False

    print(usernames, hostname)

    heartBeat_Thread = Thread(
        name="HeartBeat-Thread",
        target=HeartBeat.main, 
        args=(
            client_addr[0], 
            ADDR[1]+(len(clients)-1), 
            lambda e=None: changeExit(e),
        ), 
        daemon=True
    )

    clients_HeartBeats[username] = [False, heartBeat_Thread]
    clients_HeartBeats[username][1].start()
    delExit = False

    # Check to see if Thread is alive
    def checkForPulse():
        global checkpulsexit

        if clients_HeartBeats[username][1].is_alive():
            return True
        else:
            checkpulsexit = True
            return False

    # Change clients_HeartBeats[username][0] from the Thread
    def changeExit(value=None, username=usernames[hostname]):
        global clients_HeartBeats

        if value != None:
            clients_HeartBeats[username][0] = True
            return clients_HeartBeats[username][0]
        else:
            return clients_HeartBeats[username][0]

    # tell everyone that the user joined the chat
    msg = f"{username} has joined the chat!"
    print(f"Amount of pepole conected: {len(clients)}")
    broadcast(bytes(msg, "utf8"))

    while True and checkForPulse():

        try:
            _ = clients[client]
        except:
            delExit = True
            del usernames[hostname]
            del clients_HeartBeats[username][1]
            clients_HeartBeats[username][0] = True
            client.close()
            break

        # recive a message  
        try:
            msg = client.recv(BUFSIZ)
            # print(f"'{msg.decode()}' recived from: '{client_addr[0]}:{client_addr[1]}'")
        except:
            msg = None

        if msg != None and checkForPulse():
            # if the message is not quit then send msg
            if msg != bytes("{quit}", "utf8") and msg != bytes("{serverquit}", "utf8") and checkForPulse():
                try:
                    if checkForPulse():
                        broadcast(msg, username+": ")
                    else:
                        raise Exception
                except:
                    # print("EXIT at line 394")
                    del clients[client]
                    del usernames[hostname]
                    del clients_HeartBeats[username][1]
                    clients_HeartBeats[username][0] = True
                    client.close()
                    break
            

            # if the message is for the server to shutdown
            elif msg == bytes("{serverquit}", "utf-8") and checkForPulse():
                print("Kicking everyone from server")
                try:
                    msg = bytes("{quit}", "utf-8")
                    broadcast(msg, msgTF=False)
                except:
                    # print("EXIT at line 410")
                    del clients[client]
                    del usernames[hostname]
                    del clients_HeartBeats[username][1]
                    clients_HeartBeats[username][0] = True
                    client.close()
                    break
                

            # if the message is quit then
            elif msg == bytes("{quit}", "utf-8") and checkForPulse():
                try:
                    # close the client conection
                    client.send(bytes("[MSG] {quit}", "utf8"))
                finally:
                    # print("EXIT at line 425")
                    del clients[client]
                    del usernames[hostname]
                    del clients_HeartBeats[username][1]
                    clients_HeartBeats[username][0] = True
                    client.close()

                    # tell everyone that they have left
                    broadcast(bytes(f"{username} has left the chat.", "utf8"))

                    # close their client down
                    break
    
    if checkpulsexit == True:
        # print("EXIT in if at line 439")
        del clients[client]
        del usernames[hostname]
        del clients_HeartBeats[username][1]
        clients_HeartBeats[username][0] = True
        del clients_HeartBeats[username]
        client.close()

    elif delExit == True:
        del clients_HeartBeats[username]
    
    del hostnames[hostname]
    print(f"Amount of pepole conected: {len(clients)}")


def broadcast(msg, prefix="", msgTF=True):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    global clients, usernames

    usernames_of_clients = [usernames[n] for n in usernames]

    # add the send note "[MSG] " to prefix before sending
    # this is used to tell if it is a message or a diffrent data type
    if msgTF == True:
        prefix = "[MSG] " + prefix

    # sends a message to all users
    delsocks = []
    for pos, sock in enumerate(clients):
        # print(f"Clients username: '{usernames_of_clients[pos]}'")
        # print(f"Pos: '{pos}'")
        # print(f"Len of clients heartbeats: '{len(clients_HeartBeats)}'")
        # print(f"Len of usernames_of_clients: '{len(usernames_of_clients)}'")
        # print(f"Len of usernames_of_clients[pos]: '{len(usernames_of_clients[pos])}'")
        # print(f"Len of '{len(clients_HeartBeats[usernames_of_clients[pos]])}'")
        if clients_HeartBeats[usernames_of_clients[pos]][1].is_alive():
            sock.send(bytes(prefix, "utf8")+msg)
            # print(f"Sending: '{prefix+(msg.decode())}'")
        else:
            print(f"Username: '{usernames_of_clients[pos]}' is being delted")
            delsocks.append(clients[sock])
    
    if len(delsocks) > 0:
        for sock in delsocks:
            del clients[sock]

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections, daemon=True)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()

