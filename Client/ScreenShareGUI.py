import pygame
from socket import socket
import ScreenShareSender as sender
#import chatAppClient as Client
from threading import Thread

class button():
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

class screen(pygame.Surface):
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
            pass
        
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
WIN = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
Sharing_Screen = False
screens = []

MainMenuButtons = [
    button(
        (255, 0, 0), # color
        50, # x
        int(WIN.get_height()/2), # y
        150, # width
        30, # height
        "View Screens" # text
    ),

    button(
        (255, 0, 0), # color
        int(WIN.get_width()-(50 + 180)), # x
        int(WIN.get_height()/2), # y
        180, # width
        30, # height
        "Sharing controls", # text
        function=switchScreenTo, # function
        args="screen share options" # args
    ),

    button(
        (255, 0, 0), # color 
        int(WIN.get_width()/2)-int((80/2)+15), # x
        int(WIN.get_height()/2)+int(30*5), # y
        80, # width
        30, # height
        "Quit", # text
        function=quit # function
    )
]

MainMenuScreen = screen((69, 189, 60), "MAIN MENU", buttons=MainMenuButtons, size=SIZE)
screens.append(MainMenuScreen)

ScreenShareButtons = [
    button((0, 255, 0), 50, 50, 150, 30, "Start sharing"),
    button((255, 0, 0), 100, 100, 150, 30, "Stop sharing")
]
ScreenShareControlScreen = screen((69, 189, 60), "SCREEN SHARE OPTIONS", buttons=ScreenShareButtons, size=SIZE)
screens.append(ScreenShareControlScreen)
ScreenShareControlScreen.active = False
# screenShareThread = Thread(target=sender.main, args=(Client.HOST, Client.PORT,))

run = True
while run:
    clock.tick(60)

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

