from socket import socket
from select import select


def main(addr, stop):

    addr = (addr[0], addr[1]+1)

    HeartBeat = socket()
    HeartBeat.bind(addr)

    HeartBeat.listen(1)

    client, addr = HeartBeat.accept()

    msg = 5
    client.sendall(
        msg.to_bytes(
            ((msg.bit_length()+7)//8),
            byteorder="big"
        )
    )

    client.settimeout(2.0)

    pings = 0

    while pings != 10:
        if stop() == False:
            if hi(client, addr, pings):
                if hey(client, addr, pings):
                    if pings > 0:
                        pings = 0

                else:
                    pings += 1

            else:
                pings += 1
        
        else:
            break

    if pings == 10:
        print(f"[NOTICE] Sent {pings} pings to '{addr[0]}:{addr[1]}' and recived to response")
        print(f"[NOTICE] Closeing connection to: '{addr[0]}:{addr[1]}'")

    else:
        print(f"[NOTICE] Closeing connection to: '{addr[0]}:{addr[1]}'")
        print(f"[NOTICE] Outside source is terminating HeartBeat to '{addr[0]}:{addr[1]}'")


def hi(client, addr, pings):
    try:
        msg = client.recv(1024).decode("utf-8")
        if msg != "Hey!":
            raise TimeoutError

    except TimeoutError:
        print(f"[NOTICE] Ping from: '{addr[0]}:{addr[1]}' failed. Attempt '{pings}/10'")
        return False
    
    return True


def hey(client, addr, pings):
    try:
        client.sendall(bytes("Hey!", "utf-8"))

    except TimeoutError:
        print(f"[NOTICE] Ping to: '{addr[0]}:{addr[1]}' failed. Attempt '{pings}/10'")
        return False
    
    return True