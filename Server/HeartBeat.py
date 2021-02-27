from socket import socket
from select import select


def main(ip, port, stop):

    addr = (ip, port+1)

    client = socket()

    print(f"[HEARTBEAT] HeartBeat attempting to connect to: '{addr[0]}:{addr[1]}'")
    client.settimeout(None)
    client.connect(addr)

    e = int.from_bytes(
        client.recv(1), 
        byteorder="big"
    )

    if e != 5:
        client.close()
        return
    
    print(f"[HEARTBEAT] HeartBeat connection established to: '{addr[0]}:{addr[1]}'")

    client.settimeout(2.0)

    pings = 0

    while pings < 10:
        if stop() == False:
            if hey(client, addr, pings, stop):
                if hi(client, addr, pings, stop):
                    if pings > 0:
                        pings = 0

                else:
                    pings += 1

            else:
                pings += 1
        
        else:
            break
    
    if pings >= 10:
        print(f"[NOTICE] Sent {pings+1} pings to '{addr[0]}:{addr[1]}' and recived to response")
        print(f"[NOTICE] Closing connection to: '{addr[0]}:{addr[1]}'")
    else:
        print(f"[NOTICE] Closing connection to: '{addr[0]}:{addr[1]}'")
        print(f"[NOTICE] Outside source is terminating HeartBeat to: '{addr[0]}:{addr[1]}'")

def hi(client, addr, pings, stop):
    try:
        msg = client.recv(1024).decode("utf-8")
        if msg != "Hey!":
            raise TimeoutError

    except:
        if stop() == False:
            print(f"[NOTICE] Ping from: '{addr[0]}:{addr[1]}' failed. Attempt '{pings+1}/10'")
        return False
    
    return True


def hey(client, addr, pings, stop):
    try:
        client.sendall(bytes("Hey!", "utf-8"))

    except:
        if stop() == False:
            print(f"[NOTICE] Ping to: '{addr[0]}:{addr[1]}' failed. Attempt '{pings+1}/10'")
        return False
    
    return True