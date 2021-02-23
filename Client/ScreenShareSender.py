from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread
from zlib import compress
from mss import mss
from PIL import Image


WIDTH = 1900
HEIGHT = 1000
RECT = {"top": 0, "left": 0, "width": WIDTH, "height": HEIGHT}


def main(host="0.0.0.0", port=80):

    # setup the sending socket
    sender = socket()
    sender.connect((host, port))

    sender.recv(1024)

    ip = gethostbyname(gethostname())

    # tell the server that im a screenshare account
    sender.sendall(bytes(f"[SCREENSHARE_{ip}_S]", "utf-8"))
    print(f"Sending: '[SCREENSHARE_{ip}_S]'")

    # start the main process
    screenshare_picture_taker(sender)

def send_img(img, sender):
    # compress the image after resizeing it
    # to an apropriet value 
    # compression level can be 0-9
    imsize = (600, 600)
    image = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
    image.resize(imsize)
    pixels = image.tobytes("raw", "RGB") # b'...'
    #print(len(pixels)) # 5700000
    pixels = compress(pixels, 6)
    #print(len(pixels)) # 252259

    # send the size of the image
    sender.sendall(bytes(str(imsize[0]), "utf-8"))
    print(f"Sending: '{imsize[0]}'")

    sender.sendall(bytes(str(imsize[1]), "utf-8"))
    print(f"Sending: '{imsize[1]}'")

    # send the size of pixels length
    size = len(pixels) # 418912, 252259
    #print(size)
    size_len = (size.bit_length() + 7) // 8 # 3
    #print(size_len)

    sender.send(bytes([size_len]))
    print(f"Sending: '{[size_len]}'")

    # send the pixels length
    size_bytes = size.to_bytes(size_len, "big")
    sender.send(size_bytes)
    print(f"Sending: '{size_bytes}'")

    # send the pixels
    sender.sendall(pixels)
    print(f"Sending: '{str(pixels)[:10]}...'")

def screenshare_picture_taker(sender):
    import ScreenShareGUI as GUI
    with mss() as sct:
        while GUI.Sharing_Screen and GUI.ThreadsOn:
            # send a continue signal
            sender.sendall(bytes("True", "utf-8"))
            print("Sending: 'True'")

            # capture the screen
            img = sct.grab(RECT)
            send_img(img, sender)
        
        # send a stop sharing signal
        sender.sendall(bytes("False", "utf-8"))
        print("Sending: 'Fasle'")

           




