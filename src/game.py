import sys
import rle
import pygame
import numpy

import gameoflife

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

CELL_LENGTH = 10
CELL_IMAGE = pygame.Surface([CELL_LENGTH, CELL_LENGTH])
CELL_IMAGE.fill(BLACK)

GOL_TICK = pygame.USEREVENT + 0

SCREEN_X = 800
SCREEN_Y = 600

class RestartException(Exception):
    pass


class Character(pygame.sprite.Sprite):
    # Dir: X, Y
    DSPEED = 8
    G = CELL_LENGTH / 10
    MAX_SPEED = CELL_LENGTH - 2

    def __init__(self, gol, door, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([CELL_LENGTH, CELL_LENGTH]) 
        self.image.fill(RED)
       
        self.rect = self.image.get_rect()
        self.x, self.y = x * CELL_LENGTH, y * CELL_LENGTH
        self.vx = 0
        self.vy = 0
        self.double_jump_available = False
        
        self.gol = gol
        self.door = door

    def Tick(self):
        """ Retrun value is if won."""
        # Check whether done.
        won = self.door.Win(self.rect)
        if won:
            print "WIN"
            return True

        newX = self.x + self.vx
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
        return False

    def MoveInDirection(self, direction):
        if not direction:
            return
        
        if direction == "LEFT":
            self.vx = -Character.DSPEED
        elif direction == "RIGHT":
            self.vx = Character.DSPEED
        elif direction == "SPACE":
            if self.vy == 0:
                self.vy = -Character.DSPEED
            elif self.double_jump_available:
                self.vy = -Character.DSPEED
                self.double_jump_available = False
                self.image.fill(RED)


    def StopMovement(self, direction):
        if direction in ["LEFT", "RIGHT"]:
            self.vx = 0

    def StopFalling(self):
        self.vy = 0
        self.double_jump_available = True
        self.image.fill(BLUE)


class Door(pygame.sprite.Sprite):
    # Dir: X, Y
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([CELL_LENGTH, CELL_LENGTH * 2]) 
        self.image.fill(GREEN)
       
        self.rect = self.image.get_rect()
        self.x, self.y = x * CELL_LENGTH, y * CELL_LENGTH

    def Tick(self):
        pass

    def Win(self, character_sprite_rect):
        # Only call after the camera worked.
        return self.rect.colliderect(character_sprite_rect)


class Camera(object):
    FOLLOW_BORDER_WIDTH = 200
    FOLLOW_SPEED = 6
    def __init__(self, rect):
        self.rect = rect
    
    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
    
    def follow_sprite(self, sprite):
        """
        assumes that sprite.rect was updated recently, so run only after draw()
        """
        if sprite.rect.left < self.FOLLOW_BORDER_WIDTH:
            self.rect.x -= self.FOLLOW_SPEED
        if sprite.rect.right > self.rect.w - self.FOLLOW_BORDER_WIDTH:
            self.rect.x += self.FOLLOW_SPEED
        if sprite.rect.top < self.FOLLOW_BORDER_WIDTH: 
            self.rect.y -= self.FOLLOW_SPEED
        if sprite.rect.bottom > self.rect.h - self.FOLLOW_BORDER_WIDTH:
            self.rect.y += self.FOLLOW_SPEED
    
    def draw(self, sprites, screen):
        group = pygame.sprite.Group()
        for sprite in sprites:
            sprite.rect.x, sprite.rect.y = sprite.x - self.rect.x, sprite.y - self.rect.y
            group.add(sprite)
        group.draw(screen)
    
    def xy(self):
        return self.rect.x, self.rect.y

    def out_of_screen(self, character_sprite):
        return character_sprite.rect.bottom > self.rect.height


class GameOfLife(object):
    def __init__(self, initial):
        self._state = numpy.array(initial, dtype=int)

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
        for y in xrange(SCREEN_Y / CELL_LENGTH + 2):
            for x in xrange(SCREEN_X / CELL_LENGTH + 2):
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

def go(level, player_position, door_position):
    screen = pygame.display.set_mode([SCREEN_X, SCREEN_Y])
    clock = pygame.time.Clock()

    gol = GameOfLife(level)
    level = None

    sprites = pygame.sprite.Group()
    door = Door(*door_position)
    character = Character(gol, door, *player_position)
    sprites.add(character)
    sprites.add(door)

    camera = Camera(pygame.Rect((player_position[0] - 20) * CELL_LENGTH, (player_position[1] - 20) * CELL_LENGTH, SCREEN_X, SCREEN_Y))
    
    done = False
    pygame.time.set_timer(GOL_TICK, 600)
    pygame.time.set_timer(PLAYER_TICK, 50)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == GOL_TICK:
                gol.next_state()
            elif event.type == PLAYER_TICK:
                done = character.Tick()
            elif event.type == pygame.KEYDOWN:
                eventKey = PYGAME_KEY_TO_DIR.get(event.key, None)
                if eventKey:
                    character.MoveInDirection(eventKey)
                if event.key == pygame.K_p:
                    pause()
                elif event.key == pygame.K_r:
                    return go(level, player_position, door_position)
                elif event.key == pygame.K_q:
                    done = True
                elif event.key == pygame.K_s:
                    character.StopFalling()
            elif event.type == pygame.KEYUP:
                eventKey = PYGAME_KEY_TO_DIR.get(event.key, None)
                character.StopMovement(eventKey)

        screen.fill(WHITE)
        
        gol.draw(camera, screen)
        camera.draw(sprites, screen)
        
        camera.follow_sprite(character)
        if camera.out_of_screen(character):
            print "GAME OVER."
            done = True

        clock.tick(20)
        pygame.display.flip()

def main():
    gol, player, door = rle.load(sys.argv[1])
    pygame.init()
    try:
        go(gol, player, door)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
else:
    print __name__
