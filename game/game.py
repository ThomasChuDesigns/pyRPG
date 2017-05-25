import pygame as pg
import mobs,items,sprite,ui
from events import EventListener
import world




class Game:
    bg = pg.Color('black')
    fg = pg.Color('white')
    def __init__(self, surface):

        self.windowScreen = surface
        self.windowSize = surface.get_size()

        self.end = False
        self.running = True
        self.events = EventListener(self)
        self.hud = HUD(surface)
        self.map = world.Dungeon([32,32])
        self.itemManager = items.ItemController('data/items.json')

        self.player = mobs.Player(self.map.spawn[0],self.map.spawn[1])
        self.player.inventory.addItem(self.itemManager.getItem(0))

        self.entities = sprite.EntityGroup()
        self.entities.add([
            self.itemManager.getItem(0).drop(64, 64),
            self.itemManager.getItem(5).drop(64, 256),
            self.itemManager.getItem(6).drop(64, 512)
        ])
        self.entities.add(mobs.Goblin(256,256),mobs.Skeleton(512,512),mobs.Skeleton(400,400),self.player)

        self.camera = Camera(surface.get_size(), self.map.getWorldSize(), self.player)
        self.gui = ui.InventoryGUI(self.windowScreen,self.player.inventory)

        pg.key.set_repeat(5,5)

    def run(self):
        clock = pg.time.Clock()
        while self.running:
            dt = clock.tick(60)

            pg.display.set_caption('%s %i fps' % ('pyLota Alpha Build:', clock.get_fps()//1))

            self.render()
            self.events.handleEvent()
            self.update(dt)

    def update(self,dt):
        self.entities.update(self.map,dt)
        self.gui.update()


    def render(self):
        # Clear Screen
        self.windowScreen.fill(Game.bg)

        # Draw components here
        self.map.render(self.windowScreen,self.camera)
        self.entities.draw(self.windowScreen,self.camera)

        self.gui.draw()

        # End Game
        if not self.entities.has(self.player):
            self.end = True
            panel = pg.Surface([400,100])
            panel.fill(pg.Color(135,27,51))
            panel.set_alpha(200)
            string_size = ui.StringRenderer.getStringSize(self,'You are Dead!',48)
            ui.StringRenderer.drawString(self,panel, 'You are Dead!', ((400 - string_size[0])//2,(100 - string_size[1])//2),48)

            self.windowScreen.blit(panel,((self.windowSize[0] - 400)//2,(self.windowSize[1] - 100)//2))

        pg.display.update()

    def getCurrentMap(self):
        return self.map

    def loadMap(self,file):
        self.map = World(self.windowScreen,file)


class Camera:
    def __init__(self, screenSize, worldSize, target):
        '''
        :param screenSize: tuple
        :param worldSize: tuple
        :param target: Game object for camera to follow
        '''
        self.windowSize = screenSize
        self.world = worldSize
        self.target = target

        self.offset = []
        self.moveCamera()

    def isVisible(self,position):
        """
        checks if a pygame.Rect() object is in the self.view
        :param rect: pygame.Rect()
        :return: bool
        """
        return (position[0] - self.offset[0] >= 0) and (position[1] - self.offset[1] >= 0) and \
               (position[1] - self.offset[1] <= self.windowSize[0]) and (position[1] - self.offset[1] <= self.windowSize[1])

    def getOffsetPosition(self,rect):
        return (rect.center[0] - self.offset[0], rect.center[1] - self.offset[1])


    def getView(self):
        # returns the camera position
        return (int(self.offset[0]), int(self.offset[1]))

    def moveCamera(self):
        # moves the camera by x and y
        # -x,y are integers
        targetPos = self.target.getPosition()
        self.offset = [targetPos[0] - self.windowSize[0] // 2, targetPos[1] - self.windowSize[1] // 2]

        # Bounds of the World
        for coord in range(2):
            if self.offset[coord] < 0:
                self.offset[coord] = 0
            elif self.offset[coord] > self.world[coord] - self.windowSize[coord]:
                self.offset[coord] = self.world[coord] - self.windowSize[coord]

    def drawRectangle(self,surface,color,rect):
        orect = pg.Rect((rect.topleft[0] - self.offset[0], rect.topleft[1] - self.offset[1]),rect.size)
        pg.draw.rect(surface,color,orect,1)

class HUD():
    sprite_size = [16,16]
    def __init__(self,surface):
        self.surface = surface
        self.spritesheet = sprite.Spritesheet('hud.png')
        self.font = pg.font.Font(pg.font.get_default_font(),16)

    def drawString(self, position, string, color = pg.Color('white')):
        text = self.font.render(string,1,color)
        self.surface.blit(text,position)

    def drawImage(self,image,position,scale = [64,64]):
        # Prints a surface on screen
        if image:
            pg.draw.rect(self.surface,pg.Color('cyan'),self.surface.blit(pg.transform.scale(image,scale),position),1)
        else:
            pg.draw.rect(self.surface, pg.Color('cyan'), pg.Rect(position,scale),1)
    def drawHUDImage(self,imagePosition,position,scale = [64,64]):
        # Draws an image from the hud spritesheet
        image = pg.transform.scale(self.spritesheet.getSprite(HUD.sprite_size,imagePosition[0],imagePosition[1]),scale)
        pg.draw.rect(self.surface,pg.Color('black'),self.surface.blit(image,position),1)




