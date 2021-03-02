from socket import socket
from select import select
import time


def main(ip, port, stop, msgs, status):

    # Setup
    if True:
        status("Pinging...")

        addr = (ip, port+1)

        client = socket()

        client.settimeout(None)
        client.connect(addr)

        e = int.from_bytes(
            client.recv(1), 
            byteorder="big"
        )

        if e != 5:
            client.close()
            return
        
        msgs(f"[HEARTBEAT] HeartBeat connection established to:\n\t'{addr[0]}:{addr[1]}'")

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
            
            if pings == 0:
                status("Conected...")

            else:
                status(f"Pinging...\tAttempt: {pings}/10")

        else:
            break
    
    if pings >= 10:
        msgs(f"[TERMINATING] Becuase Server sent: '{pings}' pings and recived no response")
        msgs(f"[TERMINATING] Closing connection to:\n\t'{addr[0]}:{addr[1]}'")
        status("Terminated...")
        stop(True)
    else:
        msgs(f"[TERMINATING] HeartBeat to:\n\t'{addr[0]}:{addr[1]}'")
        status("Terminated..")

def hi(client, addr, pings, stop, msgs):
    try:
        msg = client.recv(1024).decode("utf-8")
        if msg != "Hey!":
            raise TimeoutError

    except:
        if stop() == False:
            msgs(f"Ping from: '{addr[0]}:{addr[1]}' failed.\n\tAttempt '{pings+1}/10'")
        return False
    
    return True


def hey(client, addr, pings, stop, msgs):
    try:
        client.sendall(bytes("Hey!", "utf-8"))

    except:
        if stop() == False:
            msgs(f"Ping to: '{addr[0]}:{addr[1]}' failed.\n\tAttempt '{pings+1}/10'")
        return False
    
    return True