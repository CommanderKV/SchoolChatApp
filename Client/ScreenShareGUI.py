import pygame
from socket import socket
import ScreenShareSender as sender
from mss import mss
#import chatAppClient as Client
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
    
    def draw(self, win):
        if self.thisPc is True:
            with mss() as sct:
                width = self.get_size()[0]
                height = self.get_size()[1]

                rect = sender.RECT
                img = sct.grab(rect)
                image = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
                image.resize((width, height))
                pixels = bytes(image.getdata())
                img = pygame.image.fromstring(pixels, (width, height))
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

pygame.font.init()
pygame.init()
SIZE = (600, 500)
screens = []
Sharing_Screen = False
OnOff = False
Live = False
TIMER = 0
RUN = True

def Main():
    global TIMER, RUN, Live, OnOFF, Sharing_Screen, screens
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

    ViewScreensButtons = [
        Button(
            (255, 0, 0), # color
            0, # x
            0, # y
            100, # width
            30, # height
            "Back", # text
            function=switchScreenTo, # function
            args="main menu" # args
        )
    ]

    ViewScreensScreen = Screen((69, 189, 60), "VIEW SCREEN SHARES", buttons=ViewScreensButtons, size=SIZE)
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
            size=(500, 400)
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
    # screenShareThread = Thread(target=sender.main, args=(Client.HOST, Client.PORT,))

    while RUN:
        clock.tick(60)

        if pygame.time.get_ticks()-TIMER > 1000:
            TIMER = pygame.time.get_ticks()
            if Live is True:
                OnOff = True if OnOff == False else False
                if OnOff is True:
                    ScreenShareControlScreen.buttons[0].color = (0, 255, 0)
                else:
                    ScreenShareControlScreen.buttons[0].color = (255, 0, 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for screen in screens:
                    if screen.active is True:
                        for button in screen.buttons:
                            if button.isOver(pygame.mouse.get_pos()) is True:
                                button.function(button.args) if button.args != None else button.function()

        
        # update the window
        winUpdate(WIN, screens)

    quit()

Main()
