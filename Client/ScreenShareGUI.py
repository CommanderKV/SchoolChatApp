import pygame
from socket import socket, gethostname, gethostbyname
import ScreenShareSender as sender
from mss import mss
from threading import Thread, Condition
from zlib import decompress
from PIL import Image

class Button():
    def __init__(self, color, x, y, width, height, text='', function=None, args=None):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.function = function
        self.args = args

    def draw(self,  win, outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 30)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False


class screenshare(pygame.Surface):
    def __init__(self, x, y, thisPc=True, pos=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thisPc = thisPc
        self.x = x
        self.y = y
        self.bg = (0, 0, 0)
        self.pos = pos
        self.img = None
        self.font = pygame.font.SysFont("comicsans", 40)
        self.drawingThread = False

        if self.thisPc is False:
            global host, port

            # make a socket
            self.reciver = socket()
            self.reciver.connect((host, port))

            # recive the welcome message
            self.reciver.recv(1024)

            # tell the server that i am looking to recive data
            ip = gethostbyname(gethostname())
            self.reciver.sendall(bytes(f"[SCREENSHARE_{ip}_R]", "utf-8"))
    
    def generateImg(self, surface):
        global Live

        self.img = surface
        

    def drawPreview(self):
        def makeSurface(screens, genIMG):
            import time
            start = time.time()

            run = True
            while run:
                
                if (time.time()-start) >= 0.5:
                    start = time.time()
                    for screen in screens():
                        if screen.topic == "SCREEN SHARE OPTIONS":
                            if screen.active is False:
                                run = False
            
                with mss() as sct:
                    width = self.get_size()[0]
                    height = self.get_size()[1]

                    rect = sender.RECT
                    img = sct.grab(rect)
                    image = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
                    image = image.resize((width, height))

                    pixels = image.tobytes("raw", "RGB")
                    size = (width, height)

                    img = pygame.image.fromstring(pixels, size, "RGB")
                    genIMG(img)
        
        screensAcess = lambda : screens
        genIm = lambda img=None : self.generateImg(img)
        self.drawingThread = Thread(
            target=makeSurface, 
            args=(
                screensAcess,
                genIm,
            ), 
            daemon=True
        )

        self.drawingThread.start()
                

    def draw(self, win):
        global Live

        #self.fill(self.bg)
        if self.thisPc is True:
            if self.drawingThread == False:
                self.drawPreview()
            elif self.drawingThread.is_alive() is False:
                self.drawPreview()

        else:
            # tell the server the screenshare we want
            pos = self.pos+1
            pos = pos.to_bytes(
                ((pos.bit_length()+7)//8), 
                byteorder="big"
            )
            # send the length of pos
            pos_len = ((pos.bit_length()+7)//8)
            self.reciver.sendall(pos_len.to_bytes(
                ((pos_len.bit_length()+7)//8), 
                byteorder="big"
            ))

            # send the number
            self.reciver.sendall(pos)
            print(f"Sending: '{self.pos}, {pos}'")

            # tell the server that we are still here
            self.reciver.sendall(bytes("True", "utf-8"))
            print(f"Sending: 'True'")

            # get the username from the server
            username = self.reciver.recv(1024).decode("utf-8")
            print(f"Recived: '{username}'")

            # get pixels len length
            pixels_length_len = int.from_bytes(
                self.reciver.recv(1), 
                byteorder="big"
            )
            print(f"Recived: '{pixels_length_len}'")

            # get pixels len
            pixels_len = int.from_bytes(
                self.reciver.recv(pixels_length_len), 
                byteorder="big"
            )
            print(f"Recived: '{pixels_len}'")

            # get the pixels from the server
            pixels = decompress(self.reciver.recv(pixels_len))
            print(f"Recived: '{str(pixels)[:10]}...'")

            # get the image size from the server
            imsize1 = int.from_bytes(self.reciver.recv(1), byteorder="big")
            imsize2 = int.from_bytes(self.reciver.recv(1), byteorder="big")
            imsize = (int(imsize1)*100, int(imsize2)*100)
            print(f"Recived: '{imsize}'")

            # get the type of image from the server
            imType = self.reciver.recv(1024).decode("utf-8")
            print(f"Recived: '{imType}'")

            img = self.image.fromstring(pixels, imsize, imType)
            self.blit(img, (0, 0))

            text = self.font.render(username, 1, (255, 255, 255))
            self.blit(
                text, 
                (
                    (self.get_height()-(text.get_height()+10)), 
                    (self.get_width()-(text.get_width()+10))
                )
            )

            self.generateImg(self)

        if self.img != None:
            win.blit(self.img, (self.x, self.y))

        if self.thisPc is True:
            try:
                text = self.font.render(
                    "Preview" if Live is False else "Live", 
                    1, 
                    (255, 255, 255) if Live is False else (255, 83, 56)
                )
            except:
                pygame.font.init()
                self.font = pygame.font.SysFont("comicsans", 40)

                text = self.font.render(
                    "Preview" if Live is False else "Live", 
                    1, 
                    (255, 255, 255) if Live is False else (255, 83, 56)
                )

            win.blit(
                text, 
                (
                    int(self.x + (self.get_width() - (text.get_width() + 10))), 
                    int(self.y + (self.get_height() - (text.get_height() - 2)))
                )
            )


class Screen(pygame.Surface):
    def __init__(self, backgroundColor, topic, buttons=[], screenshares=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buttons = buttons
        self.bgColor = backgroundColor
        self.screenshares = screenshares
        self.active = True
        self.topic = topic.upper()
    
    def draw(self, win):
        self.fill(self.bgColor)

        # draw each button in the buttons list if there is any
        if len(self.buttons) > 0:
            for button in self.buttons:
                button.draw(self)
        
        # draw each screen share if there are any
        if len(self.screenshares) > 0:
            for ScreenShare in self.screenshares:
                ScreenShare.draw(self)
        
        # add screen to win
        win.blit(self, (0, 0))


def startScreenShare(addr):
    global Live, Sharing_Screen, threads

    # set live and sharing_screen to True
    host, port = addr
    Live = True
    Sharing_Screen = True

    # start a thread with the sending program on it
    name = f"Sender.main/SendingScreenShare-Thread"
    t = Thread(
        name=name,
        target=sender.main, 
        args=(
            host, 
            port,
        ), 
        daemon=True
    )
    threads["sender.main"] = t
    t.start()

def stopScreenSharing():
    global Live, Sharing_Screen, threads

    threads.pop("sender.main")

    # set live and sharing_screen to False
    Live = False
    Sharing_Screen = False

def switchScreenTo(screentopic):
    for screen in screens:
        if screen.topic == screentopic.upper():
            screen.active = True
        else:
            screen.active = False

def winUpdate(win, screens):
    win.fill((255, 255, 255))

    # drawing the current screen
    for screen in screens:
        if screen.active == True:
            screen.draw(win)

    # update the pygame window
    pygame.display.update()

def updateViewScreensScreens(ViewScreensPadding, host, port):
    import time
    global screens, OPEN, ThreadsOn, RUN

    start = time.time()
    last_Amount = float("-inf")

    while OPEN and ThreadsOn:
        sharedVars.acquire()

        if len(screens) > 0:
            if screens[1].active == True:
                if time.time() - start >= 3.0:
                    start = time.time()

                    updatedScreens = []
                    x = ViewScreensPadding
                    y = int(ViewScreensPadding*2)+30
                    
                    # make a socket and connect to the server
                    guiSocket = socket()
                    guiSocket.connect((host, port))
                    guiSocket.recv(1024)

                    ip = gethostbyname(gethostname())

                    # ask for the Amount of screens that are being shared
                    guiSocket.sendall(bytes(f"[SCREENSHARE_{ip}_A]", "utf-8"))

                    # get the length of the amount
                    length = int.from_bytes(guiSocket.recv(1), byteorder="big")

                    # get the amount of screens
                    Amount = int.from_bytes(guiSocket.recv(length), byteorder="big")

                    sizes = (
                        int(SIZE[0]//3), 
                        int(int(SIZE[1]-int(int(ViewScreensPadding*2)+30)+ViewScreensPadding)//3)
                    )
                    
                    if Amount > last_Amount:
                        for i in range(Amount):
                            updatedScreens.append(
                                screenshare(
                                    x,
                                    y,
                                    size=sizes,
                                    thisPc=False, 
                                    pos=i
                                )
                            )
                            x = (x + (sizes[0] + ViewScreensPadding)) if i != 3 or i != 6 or i != 9 else ViewScreensPadding
                            y += (sizes[1]+ViewScreensPadding) if i == 3 or i == 6 or i == 9 else 0
                    
                    last_Amount = Amount

                    screens[1].screenshares = updatedScreens
                    print(len(screens[1].screenshares))

        else:
            sharedVars.release()
            break

        sharedVars.release()

def exitProgram():
    global SIZE, screens, OnOff
    global Live, TIMER, RUN, OPEN
    global ThreadsOn, threads
    global WIN, Sharing_Screen
    
    SIZE = (600, 500)
    WIN = None
    screens = []
    Sharing_Screen = False
    OnOff = False
    Live = False
    TIMER = 0
    RUN = False
    OPEN = True
    ThreadsOn = True
    threads = {}


sharedVars = Condition()
pygame.font.init()
SIZE = (600, 500)
WIN = None
screens = []
Sharing_Screen = False
OnOff = False
Live = False
TIMER = 0
RUN = True
OPEN = True
ThreadsOn = True
threads = {}

def Main(addr):
    global threads, WIN, TIMER, RUN, OPEN, Live, OnOff, Sharing_Screen, screens, SIZE
    global host, port

    host, port = addr

    pygame.init()
    WIN = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()

    if True:
        MainMenuButtons = [
            Button(
                (255, 0, 0), # color
                50, # x
                int(WIN.get_height()/2), # y
                150, # width
                30, # height
                "View Screens", # text
                function=switchScreenTo, # function
                args="view screen shares" # args
            ),

            Button(
                (255, 0, 0), # color
                int(WIN.get_width()-(50 + 180)), # x
                int(WIN.get_height()/2), # y
                180, # width
                30, # height
                "Sharing controls", # text
                function=switchScreenTo, # function
                args="screen share options" # args
            ),

            Button(
                (255, 0, 0), # color 
                int(WIN.get_width()/2)-int((80/2)+15), # x
                int(WIN.get_height()/2)+int(30*5), # y
                80, # width
                30, # height
                "Quit", # text
                function=exitProgram # function
            )
        ]

        MainMenuScreen = Screen((69, 189, 60), "MAIN MENU", buttons=MainMenuButtons, size=SIZE)
        screens.append(MainMenuScreen)

        ViewScreensPadding = 20
        ViewScreensButtons = [
            Button(
                (255, 0, 0), # color
                ViewScreensPadding, # x
                ViewScreensPadding, # y
                100, # width
                30, # height
                "Back", # text
                function=switchScreenTo, # function
                args="main menu" # args
            )
        ]

        ViewScreensScreens = []

        ViewScreensScreen = Screen(
            (69, 189, 60), 
            "VIEW SCREEN SHARES", 
            buttons=ViewScreensButtons, 
            screenshares=ViewScreensScreens, 
            size=SIZE
        )

        screens.append(ViewScreensScreen)
        ViewScreensScreen.active = False

        ScreenShareControlScreenSpacing = 20
        ScreenShareButtons = [
            Button(
                (255, 0, 0), # color
                int(WIN.get_width()-(150+ScreenShareControlScreenSpacing)), # x
                int(WIN.get_height()-((30+ScreenShareControlScreenSpacing)+(30+ScreenShareControlScreenSpacing))), # y
                150, # width
                30, # height
                "Start sharing", # text
                function=startScreenShare, # function
                args=(host, port) # args
            ),

            Button(
                (255, 0, 0), # color
                int(WIN.get_width()-(150+ScreenShareControlScreenSpacing)), # x
                int(WIN.get_height()-(30+ScreenShareControlScreenSpacing)), # y
                150, # width
                30, # height
                "Stop sharing", # text
                function=stopScreenSharing # function
            ), 

            Button(
                (255, 0, 0), # color
                ScreenShareControlScreenSpacing, # x
                int(WIN.get_height()-(30+ScreenShareControlScreenSpacing)), # y
                100, # width
                30, # height
                "Back", # text
                function=switchScreenTo, # function
                args="main menu" # args
            )
        ]

        ScreenShareScreens = [
            screenshare(
                ScreenShareControlScreenSpacing, # x
                ScreenShareControlScreenSpacing, # y
                size=(WIN.get_width()-(ScreenShareControlScreenSpacing*2), 370)
            )
        ]

        ScreenShareControlScreen = Screen(
            (69, 189, 60), # color
            "SCREEN SHARE OPTIONS", # mode
            buttons=ScreenShareButtons, # buttons
            screenshares=ScreenShareScreens, # screens
            size=SIZE # size
        )

        screens.append(ScreenShareControlScreen)
        ScreenShareControlScreen.active = False

        name = "UpdateViewScreensScreens-Thread"
        t = Thread(
            name=name,
            target=updateViewScreensScreens, 
            args=(
                ViewScreensPadding, 
                host, 
                port,
            ), 
            daemon=True
        )
        threads["updateViewScreensScreens"] = t
        t.start()

    while RUN:
        clock.tick(60)
        pygame.display.set_caption("Screen Sharing")

        if pygame.time.get_ticks()-TIMER > 1000:
            TIMER = pygame.time.get_ticks()

            # if we are shareing our screen then chacge the live color box to say hey were live
            if Live is True:
                OnOff = True if OnOff == False else False
                if OnOff is True:
                    ScreenShareControlScreen.buttons[0].color = (0, 255, 0)
                else:
                    ScreenShareControlScreen.buttons[0].color = (255, 0, 0)

            elif Live is False:
                if ScreenShareControlScreen.buttons[0].color != (255, 0, 0):
                    ScreenShareControlScreen.buttons[0].color = (255, 0, 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
                Live = False
                Sharing_Screen = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for screen in screens:
                    if screen.active is True:
                        for button in screen.buttons:
                            if button.function != None:
                                if button.isOver(pygame.mouse.get_pos()) is True:
                                    button.function(button.args) if button.args != None else button.function()

        
        # update the window
        if RUN == True:
            winUpdate(WIN, screens) 
        else:
            break
    
    exitProgram()

    # set vairables that other threads are cheking for
    OPEN = False
    ThreadsOn = False
    pygame.quit()
