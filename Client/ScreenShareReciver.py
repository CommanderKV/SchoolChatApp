from socket import socket
from zlib import decompress
import pygame

WIDTH = 1900
HEIGHT = 1000

def recvall(conn, length):
    """Retrives all pixels."""

    buf = b''
    while len(buf) < length:
        data = conn.recv(length-len(buf))
        if not data:
            return data
        buf += data
    return buf

def screenShareMain(host="0.0.0.0", port=80):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    watching = True

    reciver = socket()
    reciver.connect((host, port))

    reciver.recv(1024)

    reciver.sendall(bytes(f"[SCREENSHARE_{host}_R]", "utf-8"))

    try:
        while watching:
            clock.tick(60)
            
            # checking to see if the user has tried to close this window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break
            
            # retrive the size of pixels length, the pixels length and pixels
            size_len = int.from_bytes(reciver.recv(1), byteorder="big")
            size = int.from_bytes(reciver.recv(size_len), byteorder="big")
            pixels = decompress(recvall(reciver, size))

            # create the surface that has the imagee from ths raw pixels
            img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), "RGB")

            # display the image
            screen.blit(img, (0, 0))
            pygame.display.update()
    finally:
        reciver.close()



