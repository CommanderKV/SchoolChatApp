from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread
import chatAppClient as Client
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

    # start the main process
    screenshare_picture_taker(sender)

def send_img(img, sender):
    # compress the image after resizeing it
    # to an apropriet value 
    # compression level can be 0-9
    image = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
    image.resize((600, 600))
    pixels = bytes(image.tobytes("raw", "RGB"), "utf-8")
    pixels = compress(pixels, 6)

    # send the size of pixels length
    size = len(pixels)
    size_len = (size.bit_length() + 7) // 8
    sender.send(bytes([size_len]))

    # send the pixels length
    size_bytes = size.to_bytes(size_len, "big")
    sender.send(size_bytes)

    # send the pixels
    sender.sendall(pixels)

def screenshare_picture_taker(sender):
    import ScreenShareGUI as GUI
    with mss() as sct:
        while GUI.Sharing_Screen:
            # capture the screen
            img = sct.grab(RECT)
            send_img(img, sender)

           



