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
    DSPEED = 10
    G = 2

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([CELL_LENGTH, CELL_LENGTH]) 
        self.image.fill(RED)
       
        self.rect = self.image.get_rect()
        self.x, self.y = x * CELL_LENGTH, y * CELL_LENGTH
        self.vx = None
        self.vy = None

    def Tick(self):
        if self.vx:
            self.x += self.vx
        if self.vy != None:
            self.y += self.vy
            self.vy += Character.G
        print self.vx, self.vy

    def MoveInDirection(self, direction):
        if not direction:
            return
        
        if direction == "LEFT":
            self.vx = -Character.DSPEED
        elif direction == "RIGHT":
            self.vx = Character.DSPEED
        elif direction == "SPACE" and self.vy is None:
            self.vy = -Character.DSPEED

    def StopMovement(self):
        self.vx = None

    def StopFalling(self):
        self.vy = None


class Camera(object):
    FOLLOW_BORDER_WIDTH = 100
    FOLLOW_SPEED = 4
    def __init__(self, rect):
        self._rect = rect
    
    def move(self, x, y):
        self._rect.x += x
        self._rect.y += y
    
    def follow_sprite(self, sprite):
        """
        assumes that sprite.rect was updated recently, so run only after draw()
        """
        if sprite.rect.left - self._rect.x < self.FOLLOW_BORDER_WIDTH:
            self._rect.x -= self.FOLLOW_SPEED
        if sprite.rect.right - self._rect.x > self._rect.w - self.FOLLOW_BORDER_WIDTH:
            self._rect.x += self.FOLLOW_SPEED
        if sprite.rect.top - self._rect.y < self.FOLLOW_BORDER_WIDTH:
            self._rect.y -= self.FOLLOW_SPEED
        if sprite.rect.bottom - self._rect.y > self._rect.h - self.FOLLOW_BORDER_WIDTH:
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
PLAYER_TICK = pygame.USEREVENT + 1

# This dir is for key pressess which should affect direction.
# Use diffn't dir for other functions.
PYGAME_KEY_TO_DIR = {pygame.K_LEFT : "LEFT",
                     pygame.K_RIGHT : "RIGHT",
                     pygame.K_SPACE : "SPACE"}

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
    character = Character(0, 2)
    sprites.add(character)

    camera = Camera(pygame.Rect(0, 0, SCREEN_X, SCREEN_Y))
    
    done = False
    pygame.time.set_timer(GOL_TICK, 400)
    pygame.time.set_timer(PLAYER_TICK, 50)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == GOL_TICK:
                gol.next_state()
            elif event.type == PLAYER_TICK:
                character.Tick()
            elif event.type == pygame.KEYDOWN:
                eventKey = PYGAME_KEY_TO_DIR.get(event.key, None)
                if eventKey:
                    character.MoveInDirection(eventKey)
                if event.key == pygame.K_p:
                    pause = not pause
                elif event.key == pygame.K_q:
                    done = True
                elif event.key == pygame.K_s:
                    character.StopFalling()
            elif event.type == pygame.KEYUP:
                character.StopMovement()

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
