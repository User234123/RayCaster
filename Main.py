#defining maps up here so it is out of the way
map1 = """
############################
#.......#..................#
#............#.....C.......#
#............#.............#
#..........................#
#..........................#
#..........................#
#.............#####........#
#..........................#
#..........................#
#..........................#
#P......#.................P#
############################
"""
#importing used libaries
import pygame
import math
import time
import random
#creating window
pygame.init()
is_fullScreen = input("Would you like to lauch the game in full screen y/n")
if is_fullScreen != "y":
    screenx,screeny = 600,600
    window = pygame.display.set_mode((screenx,screeny))
else:    
    window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    screenx,screeny =  pygame.display.get_surface().get_size()
#
BLOCK_ID_COUNTER = 0
#structure block instances can refer to
#this is so if i were to use textures then no duplicuts 
#of the same texture would be stored in RAM
class Block_Structure():
    def __init__(self, img, char, colour):
        global BLOCK_ID_COUNTER
        self.img = img
        self.char = char
        self.id = BLOCK_ID_COUNTER
        self.colour = colour
        BLOCK_ID_COUNTER += 1
class Block():
    def __init__(self, x,y,id, char):
        self.x = x
        self.y = y
        self.id = id
        self.char = char
        self.spawnTimer = Timer()
        self.spawnTimer.Start()
    def Update(self):
        #see if the block is going to produce enemys
        if self.char == "P":
            #produce enemys on a timer
            if self.spawnTimer.End() > max(5,15 - player.score / 2):
                enemyList.append(Enemy(self.x,self.y,"target")) 
                self.spawnTimer = Timer()
                self.spawnTimer.Start()
#defining the different types of blocks and whaat char reprsents them in the ascii map
stoneBlock = Block_Structure(None,"#",(136,140,141))
coreBlock = Block_Structure(None, "C",(255,255,0))
producerBlock = Block_Structure(None, "P",(100,0,80))
blockList = [stoneBlock, coreBlock, producerBlock]
#Class the contains the level data
class Level():
    def __init__(self, mapString):
        #converts ascii data into actual map
        self.data = [[]]
        self.enemyList = [[]]
        mapLineList = mapString.split("\n")
        for yCounter in range(1,len(mapLineList)-1):            
            for xCounter in range(len(mapLineList[1])):
                #new lines characters signel begginging of next line
                if mapLineList[yCounter][xCounter] == "\n":
                    break
                if mapLineList[yCounter][xCounter] == ".":
                    self.data[-1].append(None)
                else:
                    if mapLineList[yCounter][xCounter] == "C":
                        player.x = xCounter
                        player.y = yCounter
                    block = self.GetBlockFromChar(mapLineList[yCounter][xCounter])
                    block.x = xCounter
                    block.y = yCounter
                    self.data[-1].append(block)
                self.enemyList[-1].append(None)
            self.data.append([])
            self.enemyList.append([])
        self.data.pop()#removes last list because it is empty
        #checking map to make sure dimensions are correct
        for yCounter in range(1,len(mapLineList)-1):  
            if len(mapLineList[yCounter]) != len(mapLineList[1]):
                raise Exception("Invalid map size, size of maps x dims vairy")
        self.sizex = len(mapLineList[1])
        self.sizey = len(mapLineList) - 1
    def GetBlockFromChar(self, char):
        for b in blockList:
            if b.char == char:
                return Block(None, None, b.id, b.char)
        raise Exception("Failed to find block with char -> "+ char)
    def Update(self):
        for y in self.data:
            for x in y:
                if x != None:
                    x.Update()

class Enemy():
    def __init__(self, x,y, name):
        self.x  = x
        self.y = y
        self.name = name
        self.speed = 1
        self.health = 100
    def Update(self):
        #enemy gets faster as the game progresses
        self.speed = 1 + player.score / 2
        #return
        xDiff = player.x - self.x
        yDiff = player.y - self.y
        #avoid division by zero
        if int(xDiff) == 0 and int(yDiff) == 0:
            player.health -= 1 * spf
        if xDiff == 0 or yDiff == 0: return
        
        distance = math.sqrt(xDiff ** 2 + yDiff ** 2)
        stepCount = distance / self.speed
        self.x += (xDiff / stepCount) * spf
        self.y += (yDiff / stepCount) * spf


enemyList = []
    
RAY_SPEED_BIG = 0.2#the size of the big jumps the ray will take
RAY_SPEED_LITTLE = 0.02#size of little jumps the ray will take
MAX_STEPS = 1000#caps the number of steps so the program does not freeze
def CastRay(rayOrg, theta, level, raySpeed):
    rayXDir = raySpeed * math.cos(theta)
    rayYDir = raySpeed * math.sin(theta)
    currentRayXPos = rayOrg[0]
    currentRayYPos = rayOrg[1]
    eDist = None
    eName = None
    enemy = None
    for stepCounter in range(MAX_STEPS):
        block = level.data[math.floor(currentRayYPos)][math.floor(currentRayXPos)] 
        if block != None:
            #find rough distance to block
            #perform second ray cast to find a more accurate distance
            distance = stepCounter * raySpeed
            if raySpeed == RAY_SPEED_LITTLE:
                return distance, block.id, eDist, eName, enemy
            else:  
                #for performance firsts casts imprecise ray and once a collision is found
                #casts a more process ray so an accurate distance can still be recorded
                smallDistance, _, smallEDist, _ , _= CastRay([currentRayXPos - rayXDir,currentRayYPos - rayYDir], theta, level, RAY_SPEED_LITTLE)  
                return smallDistance + distance, block.id, eDist, eName, enemy
        for e in enemyList:
            if currentRayXPos >= e.x and currentRayXPos <= e.x + 1: 
                if currentRayYPos >= e.y and currentRayYPos <= e.y + 1: 
                    enemy = e
                    if eDist == None:
                        eDist = stepCounter * raySpeed
                        eName = e.name
                    elif stepCounter * raySpeed < eDist:
                        eDist = stepCounter * raySpeed
                        eName = e.name
        #Update the rays position
        currentRayXPos += rayXDir
        currentRayYPos += rayYDir
    return raySpeed * MAX_STEPS, None, None, None, None

class Partical():
    def __init__(self, x, y, vx, vy, spawnTime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = -1000
        self.spawnTime = spawnTime
    def Update(self):
        #apply graverty
        self.vy -= self.ay * spf
        #apply verlocity
        self.x += self.vx * spf
        self.y += self.vy * spf
    def Draw(self):
        pygame.draw.rect(window,(0,0,255),(self.x,self.y,3,3))
particalList = []

class Player():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rotz = 0
        self.speed = 2
        self.rotationSpeed = 3
        self.health = 6
        self.shotCountDown = 0
        self.score = 0
        self.shoot = False
    def Draw(self):
        self.shotCountDown -= 1
        size = 3
        pygame.draw.rect(window,(255,255,255),(screenx / 2 - size / 2, screeny / 2 - size / 2, size, size))
        if self.shoot:
            pygame.draw.rect(window,(200,50,0),(screenx / 2 - 4, screeny / 2 - 4, 8, 8))
        self.shoot = False
    def GetInput(self, level):
        keys = pygame.key.get_pressed()
        newx = self.x
        newy = self.y

        if keys[pygame.K_w]:
            newy += math.sin(self.rotz) * self.speed * spf
            newx += math.cos(self.rotz) * self.speed * spf
        if keys[pygame.K_s]:
            newy -= math.sin(self.rotz) * self.speed * spf
            newx -= math.cos(self.rotz) * self.speed * spf
        if keys[pygame.K_d]:
            newy += math.sin(self.rotz + math.pi / 2) * self.speed * spf
            newx += math.cos(self.rotz + math.pi / 2) * self.speed * spf
        if keys[pygame.K_a]:
            newy -= math.sin(self.rotz + math.pi / 2) * self.speed * spf
            newx -= math.cos(self.rotz + math.pi / 2) * self.speed * spf

        
        if level.data[math.floor(newy)][math.floor(newx)] == None:
            self.x = newx
            self.y = newy
        
    
        #rotation
        if keys[pygame.K_e]: self.rotz += self.rotationSpeed * spf
        if keys[pygame.K_q]: self.rotz -= self.rotationSpeed * spf
    def Shoot(self, level):
        if self.shotCountDown > 0: return
        self.shotCountDown = 5
        _, _, eDist, eName, enemy = CastRay([self.x,self.y],self. rotz, level, RAY_SPEED_BIG)
        self.shoot = True
        if eDist == None: return
        for edx,e in enumerate(enemyList):
            if e == enemy:
                for i in range(10):
                    vx = random.randint(-300,300) / 10
                    vy = random.randint(-500,0) / 10
                    particalList.append(Partical(screenx/2,screeny/2, vx, vy, time.time()))
                e.health -= 10
                if e.health <= 0:
                    enemyList.pop(edx)
                    self.score += 1

class Timer():
    def __init__(self):
        pass
    def Start(self):
        self.start = time.time()
    def End(self):
        return time.time() - self.start

FOV = math.pi / 2#90 degrees
RES = int(screenx / 2)# a rays is cast for each pixel on the x axis

player = Player(1,1)
level1 = Level(map1)
level1.enemyList[2][2] = Enemy(2,2,"target5")
levelList = [level1]

levelCounter = 0

#used to calculate the elapsed time over one frame
timer = Timer()
#initilise it to a value for the first frame
spf = 1
#The option the user has selected in the given menu
pickedOption = 0
#so objects in the distance dont look to dark
BASE_LIGHT = 150
#Cannot press button again untill it is released
#this is needed for menus because it would be to hard to controll
w_pressed = False
s_pressed = False
#initalize pygame fonts to defauls system font
font = pygame.font.Font(None, int(screeny / 10))
def DrawCenterText(txt, height, selected):
    if selected: c = (0,200,0)
    else: c = (0,128,0)
    texture = font.render(txt, True, c)
    fontWidth, fontHeight = font.size(txt)
    renderPos = (screenx / 2 - fontWidth / 2, height)
    if selected:
        pygame.draw.rect(window,(0,0,130),(renderPos[0],renderPos[1], fontWidth, fontHeight))
    window.blit(texture,renderPos)

def ResetMainGame():
    global player, levelCounter, enemyList, selectedMenu
    player = Player(player.x,player.y)
    levelCounter = 0
    selectedMenu = "MainMenu"
    enemyList = []
def MainGame():
    global currentLevel, timer, spf, selectedMenu
    currentLevel = levelList[levelCounter]
    pygame.display.set_caption("FPS: " + str(1/spf) + " player Health -> " + str(player.health))
    timer.Start()
    #draws the sky
    pygame.draw.rect(window,(135, 206, 235),(0,0,screenx,screeny/2))
    #draws the floor
    pygame.draw.rect(window,(202, 164, 114),(0,screeny/2,screenx,screeny/2))
    #updates the event queue so pygame responds to input and screen movement
    pygame.event.pump()
    player.GetInput(levelList[0])
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        player.Shoot(currentLevel)
    #update block's
    currentLevel.Update()
    #update all enemys
    for e in enemyList:
        e.Update()
    #update particals
    pCounter = 0
    while pCounter < len(particalList):
        if time.time() - particalList[pCounter].spawnTime > 4:
            particalList.pop(pCounter)#removes particals that have been alive for more than 4 seconds
            continue
        particalList[pCounter].Update()
        pCounter += 1
    #
    xDrawPos = 0
    drawLineWidth = int(screenx / RES)
    for i in range(RES):
        #calculate angle of the ray
        theta = (i / RES * FOV) - (FOV / 2)
        #cast the ray
        distance, blockId, eDist, eName, enemy = CastRay([player.x,player.y], theta + player.rotz, currentLevel, RAY_SPEED_BIG)
        #get block colour
        colour = blockList[blockId].colour
        #check for division by zero
        if distance == 0:
            heightOfLine = 2000 * screeny
            lighting = 255 - BASE_LIGHT
        else:
            heightOfLine = min(2000, 1/ distance) * screeny
            lighting = min(1/distance * (255 - BASE_LIGHT), 255-BASE_LIGHT)
        lighting += BASE_LIGHT
        lighting /= 255# normalize lighting between 0 and 1
        r,g,b = colour
        #Actual performs the rendering to the screen
        pygame.draw.line(window,(r*lighting, g*lighting,b *lighting),[xDrawPos, -heightOfLine + screeny / 2],[xDrawPos, heightOfLine + screeny/2], drawLineWidth)
        #if enemy hit
        if eDist != None:
            if eDist != 0:
                heightOfLine = min(2000, 1/ eDist) * (screeny / 4)
                #draws enemy ontop of wall because bottem of the enemy is transparent and so the wall behind will still need to be drawn
                pygame.draw.line(window,(255,enemy.health / 100 * 255,0),[xDrawPos, -heightOfLine + screeny / 2],[xDrawPos, heightOfLine + screeny/2], drawLineWidth)
        xDrawPos += drawLineWidth
    #draw and update all the particals
    for p in particalList:
        p.Draw()
    #draw the plays cross hair and other HUD info
    player.Draw()
    #check is player is dead
    if player.health <= 0:
        DrawCenterText("YOU DIED", screeny / 2, False)
        DrawCenterText("Enter to restart", screeny / 2 + 50, False)
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            ResetMainGame()
    #displays the kill count to the player
    window.blit(font.render("Kill Count: " + str(player.score), True, (30,30,220)), (0,0))
    pygame.display.update()
    spf = timer.End()
def MainMenu():
    global pickedOption, selectedMenu, w_pressed, s_pressed
    pygame.event.pump()
    pygame.draw.rect(window,(37, 150, 190),(0,0,screenx,screeny))
    s = 70
    DrawCenterText("Aim Game!",s,False)
    DrawCenterText("Start Game",2 * s,pickedOption == 0)
    DrawCenterText("Controlls",3 * s,pickedOption == 1)
    DrawCenterText("W/S to select different options",4 * s,False)
    DrawCenterText("Enter to select option",5 * s,False)
    DrawCenterText("Kill as many boxes as possible",6*s,False)
    DrawCenterText("They turn red as you do damage",7*s,False)
    DrawCenterText("The more you kill the harder",8*s,False)
    DrawCenterText("It becomes",9*s,False)
    #get key presses
    if pygame.key.get_pressed()[pygame.K_RETURN]:
        if pickedOption == 0: selectedMenu = "MainGame"
        elif pickedOption == 1: selectedMenu = "ControllMenu"
    if pygame.key.get_pressed()[pygame.K_w]:
        if w_pressed == False:
            pickedOption = (pickedOption - 1) % 2
            w_pressed = True
    else: w_pressed = False
    if pygame.key.get_pressed()[pygame.K_s]:
        if s_pressed == False:
            pickedOption = (pickedOption + 1) % 2
            s_pressed = True
    else: s_pressed = False

    pygame.display.update()
def ControllsMenu():
    global selectedMenu
    pygame.event.pump()
    pygame.draw.rect(window,(37, 150, 190),(0,0,screenx,screeny))
    s = 70
    DrawCenterText("WASD for movement",s,False)
    DrawCenterText("Q/E to rotate",2*s,pickedOption == 0)
    DrawCenterText("Space to shoot",3*s,pickedOption == 1)
    DrawCenterText("Press E to go back to main menu",4*s,False)
    #get key presses
    if pygame.key.get_pressed()[pygame.K_e]:
        selectedMenu = "MainMenu"
    pygame.display.update()
ResetMainGame()
run = True
while run:
    #switch between the different menues
    match selectedMenu:
        case "ControllMenu":
            ControllsMenu()
        case "MainMenu":
            MainMenu()
        case "MainGame":
            MainGame()
        #check for invalid menue name
        case _:
            raise Exception("Did not match any cases -> "+ selectedMenu)
    
