from socket import socket
from select import select
import time


def main(ip, port, stop, msgs):

    addr = (ip, port+1)

    client = socket()

    msgs(f"[HEARTBEAT] HeartBeat attempting to connect to: '{addr[0]}:{addr[1]}'")
    client.settimeout(None)
    client.connect(addr)

    e = int.from_bytes(
        client.recv(1), 
        byteorder="big"
    )

    if e != 5:
        client.close()
        return
    
    msgs(f"[HEARTBEAT] HeartBeat connection established to: '{addr[0]}:{addr[1]}'")

    client.settimeout(2.0)

    pings = 0

    while pings < 10:
        if stop() == False:
            time.sleep(0.2)
            if hey(client, addr, pings, stop, msgs):
                time.sleep(0.2)
                if hi(client, addr, pings, stop, msgs):
                    if pings > 0:
                        pings = 0

                else:
                    pings += 1

            else:
                pings += 1
        
        else:
            break
    
    if pings >= 10:
        msgs(f"[NOTICE] Sent {pings} pings to '{addr[0]}:{addr[1]}' and recived to response")
        msgs(f"[NOTICE] Closing connection to: '{addr[0]}:{addr[1]}'")
        stop(True)
    else:
        msgs(f"[NOTICE] Closing connection to: '{addr[0]}:{addr[1]}'")
        msgs(f"[NOTICE] Outside source is terminating HeartBeat to: '{addr[0]}:{addr[1]}'")

def hi(client, addr, pings, stop, msgs):
    try:
        msg = client.recv(1024).decode("utf-8")
        if msg != "Hey!":
            raise TimeoutError

    except:
        if stop() == False:
            msgs(f"[NOTICE] Ping from: '{addr[0]}:{addr[1]}' failed. Attempt '{pings+1}/10'")
        return False
    
    return True


def hey(client, addr, pings, stop, msgs):
    try:
        client.sendall(bytes("Hey!", "utf-8"))

    except:
        if stop() == False:
            msgs(f"[NOTICE] Ping to: '{addr[0]}:{addr[1]}' failed. Attempt '{pings+1}/10'")
        return False
    
    return True