import pygame
from socket import socket, gethostname, gethostbyname
import ScreenShareSender as sender
from mss import mss
from threading import Thread
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
    def __init__(self, x, y, thisPc=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thisPc = thisPc
        self.x = x
        self.y = y
        self.bg = (0, 0, 0)
    
    def draw(self, win):
        self.fill(self.bg)
        if self.thisPc is True:
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
                self.blit(img, (0, 0))
        
        win.blit(self, (self.x, self.y))


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
    global screens

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

    # get the amount of screens
    Amount = int(guiSocket.recv(1024).decode("utf-8"))

    sizes = (
        int(SIZE[0]/3), 
        int(int(SIZE[1]-int(int(ViewScreensPadding*2)+30)+ViewScreensPadding)/3)
    )

    for i in range(Amount):
        updatedScreens.append(
            screenshare(
                x,
                y,
                size=sizes,
                thisPc=False
            )
        )
        x = (x + (sizes[0] + ViewScreensPadding)) if i != 3 or i != 6 or i != 9 else ViewScreensPadding
        y += (sizes[1]+ViewScreensPadding) if i == 3 or i == 6 or i == 9 else 0

    screens[1].screenshares = updatedScreens

pygame.font.init()
SIZE = (600, 500)
screens = []
Sharing_Screen = False
OnOff = False
Live = False
TIMER = 0
RUN = True

def Main(addr):
    global TIMER, RUN, Live, OnOFF, Sharing_Screen, screens
    
    host, port = addr

    WIN = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()

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
            function=quit # function
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
    updateViewScreensScreens(ViewScreensPadding, host, port)

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
            "Start sharing" # text
        ),

        Button(
            (255, 0, 0), # color
            int(WIN.get_width()-(150+ScreenShareControlScreenSpacing)), # x
            int(WIN.get_height()-(30+ScreenShareControlScreenSpacing)), # y
            150, # width
            30, # height
            "Stop sharing" # text
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

    while RUN:
        clock.tick(60)
        pygame.display.set_caption("Screen Sharing")

        if pygame.time.get_ticks()-TIMER > 1000:
            TIMER = pygame.time.get_ticks()

            # if view screen is active then we can update the amoount of screens
            if screens[1].active == True:
                updateViewScreensScreens(ViewScreensPadding, host, port)

            # if we are shareing our screen then chacge the live color box to say hey were live
            if Live is True:
                OnOff = True if OnOff == False else False
                if OnOff is True:
                    ScreenShareControlScreen.buttons[0].color = (0, 255, 0)
                else:
                    ScreenShareControlScreen.buttons[0].color = (255, 0, 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
                quit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for screen in screens:
                    if screen.active is True:
                        for button in screen.buttons:
                            if button.isOver(pygame.mouse.get_pos()) is True:
                                button.function(button.args) if button.args != None else button.function()

        
        # update the window
        winUpdate(WIN, screens)
