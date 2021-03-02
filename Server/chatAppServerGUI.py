import pygame

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
            pygame.font.init()
            font = pygame.font.SysFont('comicsans', 30)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False


class Screen(pygame.Surface):
    def __init__(self, backgroundColor, topic, buttons=[], screenshares=[], otherSurfaces=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buttons = buttons
        self.bgColor = backgroundColor
        self.screenshares = screenshares
        self.otherSurfaces = otherSurfaces
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
        
        if len(self.otherSurfaces) > 0:
            for surface in self.otherSurfaces:
                self.blit(surface, (surface.x, surface.y))
        
        # add screen to win
        win.blit(self, (0, 0))


class TextWindow(pygame.Surface):
    def __init__(self, x, y, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y

        self.color = (255, 255, 255)
        self.fontSize = 30
        self.XPadding = 5
        self.YPadding = 5

        pygame.font.init()
        self.font = pygame.font.SysFont("comicsans", self.fontSize)

    def draw(self, text):
        self.fill((48, 48, 48))
        
        if "\t" in text:
            text = text.replace("\t", " "*10)

        if "\n" in text:
            splitText = text.split("\n")

            split_Max = int(self.get_width()-self.fontSize)+int(SIZE[0]/self.fontSize)*47
            split_Mark = int(split_Max/self.fontSize)
            print(len(splitText[0])*self.fontSize, split_Max)
            for pos, t in enumerate(splitText):
                if len(t)*self.fontSize > split_Max:
                    splitText.insert(pos+1, str(t[split_Mark:]))
                    splitText[pos] = str(t[:split_Mark])+"-"

            y = self.YPadding
            for textToRender in splitText:
                
                renderedText = self.font.render(textToRender, 1, self.color)
                self.blit(renderedText, (self.XPadding, y))
                y += self.fontSize

        else:
            text = self.font.render(text, 1, self.color)
            self.blit(text, (0, 0))


def switchScreenTo(screentopic):
    for screen in screens:
        if screen.topic == screentopic.upper():
            screen.active = True
        else:
            screen.active = False

def drawWindow(win):
    win.fill((0, 0, 0))

    for screen in screens:
        if screen.active is True:
            screen.draw(win)
    
    pygame.display.update()

def exitGUI():
    global run
    run = False

def main(usernamesLink, outputLink):
    global screens, run, SIZE

    SIZE = (800, 850)
    PADDINGX = 10
    PADDINGY = 10
    WIN = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    serverOutput = ""
    screens = []

    if True:

        serverStartScreenButtons = [
            Button(
                (255, 255, 255),
                int(SIZE[0]-200)-PADDINGX,
                int(PADDINGY),
                200,
                50,
                "Conected users",
                switchScreenTo,
                "conected users"
            ),
            Button(
                (255, 255, 255),
                PADDINGX,
                int(SIZE[1]-50-PADDINGY),
                200,
                50,
                "Stop server",
                exitGUI
            )
        ]

        serverStartScreenTextWindow = [
            TextWindow(
                PADDINGX,
                PADDINGY,
                size=((SIZE[0]-(PADDINGX*3))-200, (SIZE[1]-(PADDINGY*3)-50))
            )
        ]

        serverStartScreen = Screen(
            (0, 0, 0), 
            "SERVER START SCREEN", 
            serverStartScreenButtons, 
            size=SIZE,
            otherSurfaces=serverStartScreenTextWindow
        )

        screens.append(serverStartScreen)
        serverStartScreen.active = True

        ConectedUsersScreenButtons = [
            Button(
                (255, 255, 255),
                int(PADDINGX),
                int(SIZE[1]-PADDINGY)-50,
                200,
                50,
                "BACK",
                switchScreenTo,
                "server start screen"
            )
        ]

        ConectedUsersScreenTextWindows = [
            TextWindow(
                PADDINGX,
                PADDINGY,
                size=((SIZE[0]-(PADDINGX*3))-200, (SIZE[1]-(PADDINGY*3)-50))
            )
        ]

        ConectedUsersScreen = Screen(
            (0, 0, 0), 
            "CONECTED USERS", 
            ConectedUsersScreenButtons,
            size=SIZE,
            otherSurfaces=ConectedUsersScreenTextWindows
        )

        screens.append(ConectedUsersScreen)
        ConectedUsersScreen.active = False

    run = True
    while run:
        clock.tick()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                    for screen in screens:
                        if screen.active is True:
                            for button in screen.buttons:
                                if button.function != None:
                                    if button.isOver(pygame.mouse.get_pos()) is True:
                                        button.function(button.args) if button.args != None else button.function()

        if serverStartScreen.active is True:
            msg = outputLink()

            if len(msg) > 0:
                for msgOutput in msg:
                    serverOutput += str(msgOutput)+"\n"
                    serverStartScreenTextWindow[0].draw(serverOutput)
            outputLink(True)

        elif ConectedUsersScreen.active is True:
            usernames, clientStatus, clientIps = usernamesLink()
            
            usernamesText = ""
            for pos, username in enumerate(usernames):
                usernamesText += str(username) + "\t" + str(clientIps[pos]) + "\t" + str(clientStatus[pos]) + "\n"

            ConectedUsersScreenTextWindows[0].draw(usernamesText)

        drawWindow(WIN)
