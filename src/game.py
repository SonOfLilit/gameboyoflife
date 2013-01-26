import pygame
import numpy

import gameoflife


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

CELL_LENGTH = 16
CELL_IMAGE = pygame.Surface([CELL_LENGTH, CELL_LENGTH])
CELL_IMAGE.fill(BLACK)

GOL_TICK = pygame.USEREVENT + 0

SCREEN_X = 640
SCREEN_Y = 480


class Character(pygame.sprite.Sprite):
    # Dir: X, Y
    DIRECTIONS = {"UP":(0,2),
                  "DOWN":(0,-2),
                  "LEFT":(-2, 0),
                  "RIGHT":(2, 0)}
    def __init__(self, x, y, speed=(0, 0), acc=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([CELL_LENGTH, CELL_LENGTH]) 
        self.image.fill(RED)
       
        self.rect = self.image.get_rect()
        self.x, self.y = x * CELL_LENGTH, y * CELL_LENGTH
        self.speed = speed
        self.acc = acc

    def Tick(self):
        self.speed = (self.speed[0] + self.acc[0], self.speed[1] + self.acc[1])
        self.x += self.speed[0]
        self.y += self.speed[1]
        print "x:" , self.x
        print self.speed

    def GainAcceleration(self, direction):
        if not direction:
            return
        self.acc = self.acc + Character.DIRECTIONS[direction]
        print self.acc

    def LostAcceleration(self):
        self.acc = 0, 0

    def IsDead(self):
        # TODO: DECIDE.
        return (self.speed > -10 or
                self.cell_y < -100)


class Camera(object):
    FOLLOW_BORDER_WIDTH = 100
    FOLLOW_SPEED = 4
    def __init__(self, rect):
        self._rect = rect
    
    def move(self, x, y):
        self._rect.x += x
        self._rect.y += y
    
    def follow_sprite(self, sprite):
        if sprite.x - self._rect.x < self.FOLLOW_BORDER_WIDTH:
            self._rect.x -= self.FOLLOW_SPEED
        if sprite.x - self._rect.x > self._rect.w - self.FOLLOW_BORDER_WIDTH:
            self._rect.x += self.FOLLOW_SPEED
        if sprite.y - self._rect.y < self.FOLLOW_BORDER_WIDTH:
            self._rect.y -= self.FOLLOW_SPEED
        if sprite.y - self._rect.y > self._rect.h - self.FOLLOW_BORDER_WIDTH:
            self._rect.y += self.FOLLOW_SPEED
        
            

    def draw(self, sprites, screen):
        group = pygame.sprite.Group()
        for sprite in sprites:
            sprite.rect.x, sprite.rect.y = sprite.x - self._rect.x, sprite.y - self._rect.y
            group.add(sprite)
        group.draw(screen)
    
    def xy(self):
        return self._rect.x, self._rect.y


class GameOfLife(object):
    def __init__(self, initial):
        self._state = numpy.array(initial)

    def next_state(self):
        self._state = gameoflife.round(self._state)
    
    def draw(self, camera, screen):
        camera_x, camera_y = camera.xy()
        gol_x0 = camera_x / CELL_LENGTH
        gol_y0 = camera_y / CELL_LENGTH
        # In a height H (parts of) up to (H/object_height)+1 objects may live side-by-side.
        # True, in the case where the camera is "synchronized" with the game world it will be
        # (H/object_height), but usually there are parts of objects at top and bottom.
        for y in xrange(SCREEN_Y / CELL_LENGTH + 1):
            for x in xrange(SCREEN_X / CELL_LENGTH + 1):
                # GOL coordinates of this cell
                gol_x, gol_y = gol_x0 + x, gol_y0 + y
                
                if self._state[gol_x, gol_y]:
                    # screen coordinates of this cell with this camera
                    cell_y = -(camera_y % CELL_LENGTH) + CELL_LENGTH * y
                    cell_x = -(camera_x % CELL_LENGTH) + CELL_LENGTH * x
                    rect = pygame.Rect((cell_x, cell_y), (CELL_LENGTH, CELL_LENGTH))
                    screen.fill(BLACK, rect)
        
        

GOL_TICK = pygame.USEREVENT + 0


# This dir is for key pressess which should affect direction.
# Use diffn't dir for other functions.
PYGAME_KEY_TO_DIR = {pygame.K_LEFT : "LEFT",
                     pygame.K_RIGHT : "RIGHT"}

# TODO: Utilze this?
PYGAME_KEY_TO_FUNC = {pygame.K_p : "PAUSEKEY"}

def go():
    screen = pygame.display.set_mode([SCREEN_X, SCREEN_Y])
    clock = pygame.time.Clock()

    gol_state = numpy.zeros((800, 800))
    x, y = gameoflife.glider_round1.shape
    gol_state[:x, :y] = gameoflife.glider_round1
    gol_state[4:6, 10:12] = 1
    gol_state[10:13, 17:19] = 1

    gol = GameOfLife(gol_state)
    gol_state = None

    sprites = pygame.sprite.Group()
    character = Character(35, 28)
    sprites.add(character)

    camera = Camera(pygame.Rect(0, 0, SCREEN_X, SCREEN_Y))
    
    pygame.time.set_timer(GOL_TICK, 200)

    done = False
    pygame.time.set_timer(GOL_TICK, 400)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == GOL_TICK:
                gol.next_state()
                character.Tick()
            elif event.type == pygame.KEYDOWN:
                eventKey = PYGAME_KEY_TO_DIR.get(event.key, None)
                if eventKey:
                    character.GainAcceleration(eventKey)
                if event.key == pygame.K_p:
                    pause = not pause
                elif event.key == pygame.K_q:
                    done = True
            elif event.type == pygame.KEYUP:
                character.LostAcceleration()


        screen.fill(WHITE)
        
        gol.draw(camera, screen)
        camera.draw(sprites, screen)
        
        camera.follow_sprite(character)

        clock.tick(20)
        pygame.display.flip()

def main():
    try:
        pygame.init()
        go()
    finally:
        pygame.quit()
    
if __name__ == "__main__":
    main()
