import sys
import rle
import pygame
import numpy

import gameoflife

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

CELL_LENGTH = 30
CELL_IMAGE = pygame.Surface([CELL_LENGTH, CELL_LENGTH])
CELL_IMAGE.fill(BLACK)

GOL_TICK = pygame.USEREVENT + 0

SCREEN_X = 800
SCREEN_Y = 600

class Character(pygame.sprite.Sprite):
    # Dir: X, Y
    DSPEED = CELL_LENGTH / 2
    G = CELL_LENGTH / 10
    MAX_SPEED = CELL_LENGTH - 2

    def __init__(self, gol, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([CELL_LENGTH / 2, CELL_LENGTH / 2]) 
        self.image.fill(RED)
       
        self.rect = self.image.get_rect()
        self.x, self.y = x * CELL_LENGTH + CELL_LENGTH / 4, y * CELL_LENGTH + CELL_LENGTH / 4
        self.vx = 0
        self.vy = 0
        
        self.gol = gol

    def Tick(self):
        newX = self.x
        newY = self.y
        if self.vx:
            newX = self.x + self.vx
        if self.vy != None:
            newY = self.y + self.vy

        # if we are 16 pixels high we span from some y to y + 15, thus the -1s
        stopping = self.gol.check_bottom_collision((self.x, self.y + self.rect.height - 1),
                                                (newX, newY + self.rect.height),
                                                self.rect.width - 1)
        if stopping:
            newX = stopping[0]
            newY = stopping[1] - self.rect.height
            self.StopFalling()
        else:
            self.vy += Character.G
            if self.vy > Character.MAX_SPEED:
                self.vy = Character.MAX_SPEED

        self.x = newX
        self.y = newY

    def MoveInDirection(self, direction):
        if not direction:
            return
        
        if direction == "LEFT":
            self.vx = -Character.DSPEED
        elif direction == "RIGHT":
            self.vx = Character.DSPEED
        elif direction == "SPACE" and self.vy == 0:
            self.vy = -Character.DSPEED

    def StopMovement(self):
        self.vx = 0

    def StopFalling(self):
        self.vy = 0


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
    
    def check_bottom_collision(self, (x0, y0), (x1, y1), width):
        # TODO: rename to check_floor_collision
        """
        (x0, y0) are leftmost point of character's feet at beginning
        of movement, (x1, y1) are leftmost point of character's feet
        at end of movement with y1 incremented by 1 (so that if
        character is standing still collision with the cell below will
        keep being reported). width is width of character feet.

        returns None if no collision below, (x, y) where character
        should stop if there is collision.
        """
        if y0 >= y1:
            return None
        
        # Should be pretty easy to remove this limitation, just add a for loop
        assert y1 - y0 < CELL_LENGTH, "character falling more than a cell in a tick not supported yet"
        assert abs(x1 - x0) < CELL_LENGTH, "character crossing more than a cell horizontally in a tick not supported"
        
        
        # floor is a border between a cell and the cell below it where
        # the cell above is white and the cell below is black.
        #
        # Character collides with floor only if character's path crosses
        # floor.
        #
        # If there are no floors in rectangle including character's path,
        # no collision
        if not ((not self._at(x0, y0) and self._at(x0, y1)) or (not self._at(x0 + width, y0) and self._at(x0 + width, y1))):
            return None
        # If at end we will be wholly in white, no collision
        if not self._at(x1, y1) and not self._at(x1 + width, y1):
            return None
        # Calculate x where we cross cells on y
        y_crossing = y1 - (y1 % CELL_LENGTH)
        # Can't be division by zero because of if at beginning of function
        x_crossing = x0 + (x1 - x0) * (y_crossing - y0) / (y1 - y0)
        # now, is this collision with floor or do we pass through side?
        if ((not self._at(x_crossing, y_crossing - 1) and self._at(x_crossing, y_crossing)) or (not self._at(x_crossing + width, y_crossing - 1) and self._at(x_crossing + width, y_crossing))):
            # collision! return where character was stopped!
            return x_crossing, y_crossing
        else:
            # wasn't real floor (only diagonal changed from white to black) or passed through side
            return None
        
    def _at(self, x, y):
        """
        returns value at world x, y
        """
        gol_x = x / CELL_LENGTH
        gol_y = y / CELL_LENGTH
        return self._state[gol_x, gol_y]
    
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

def pause():
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                return

def go(level):
    screen = pygame.display.set_mode([SCREEN_X, SCREEN_Y])
    clock = pygame.time.Clock()

    gol = GameOfLife(level)
    level = None

    sprites = pygame.sprite.Group()
    character = Character(gol, 5, 0)
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
                    pause()
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
    level = rle.load(sys.argv[1])
    pygame.init()
    try:
        go(level)
    finally:
        pygame.quit()
    
if __name__ == "__main__":
    main()
