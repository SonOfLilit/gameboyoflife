import pygame
import numpy


def gol_round(Z):
    """
    From http://dana.loria.fr/doc/game-of-life.html
    """
    # find number of neighbours that each square has
    N = numpy.zeros(Z.shape)
    N[1:, 1:] += Z[:-1, :-1]
    N[1:, :-1] += Z[:-1, 1:]
    N[:-1, 1:] += Z[1:, :-1]
    N[:-1, :-1] += Z[1:, 1:]
    N[:-1, :] += Z[1:, :]
    N[1:, :] += Z[:-1, :]
    N[:, :-1] += Z[:, 1:]
    N[:, 1:] += Z[:, :-1]
    # zero the edges
    N[0,: ] = 0
    N[-1,: ] = 0
    N[:, 0] = 0
    N[:, -1] = 0
    # a live cell is killed if it has fewer than 2 or more than 3 neighbours.
    part1 = ((Z == 1) & (N < 4) & (N > 1))
    # a new cell forms if a square has exactly three members
    part2 = ((Z == 0) & (N == 3))
    return (part1 | part2).astype(int)

glider_round1 = numpy.array(
    [[0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 0, 0],
     [0, 1, 0, 1, 0, 0],
     [0, 0, 1, 1, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0]])
glider_round2 = numpy.array(
    [[0, 0, 0, 0, 0, 0],
     [0, 0, 1, 0, 0, 0],
     [0, 0, 0, 1, 1, 0],
     [0, 0, 1, 1, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0]])
assert (gol_round(glider_round1) == glider_round2).all()
# test that outer edges remain zero
glider = glider_round1
for i in xrange(20):
    glider = gol_round(glider)
square = numpy.array(
    [[0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 1, 0],
     [0, 0, 0, 1, 1, 0],
     [0, 0, 0, 0, 0, 0]])
assert (glider == square).all()


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
    FOLLOW_BORDER_WIDTH = 50
    def __init__(self, rect):
        self._rect = rect
    
    def move(self, x, y):
        self._rect.x += x
        self._rect.y += y
    
    def follow_sprite(self, sprite):
        if sprite.x + self._rect.left < self.FOLLOW_BORDER_WIDTH:
            self._rect.x += 1
        if sprite.x > self._rect.right - self.FOLLOW_BORDER_WIDTH:
            self._rect.x -= 1
        if sprite.y + self._rect.top < self.FOLLOW_BORDER_WIDTH:
            self._rect.y += 1
        if sprite.y > self._rect.bottom - self.FOLLOW_BORDER_WIDTH:
            self._rect.y -= 1
        
            

    def draw(self, sprites, screen):
        group = pygame.sprite.Group()
        for sprite in sprites:
            sprite.rect.x, sprite.rect.y = sprite.x + self._rect.x, sprite.y + self._rect.y
            group.add(sprite)
        group.draw(screen)
    
    def xy(self):
        return self._rect.x, self._rect.y



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
    x, y = glider_round1.shape
    gol_state[:x, :y] = glider_round1
    gol_state[4:6, 10:12] = 1
    gol_state[10:13, 17:19] = 1

    sprites = pygame.sprite.Group()
    character = Character(0, 0)
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
                gol_state = gol_round(gol_state)
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


        screen.fill(BLUE)
        
        camera_x, camera_y = camera.xy()
        gol_x0 = camera_x / CELL_LENGTH
        gol_y0 = camera_y / CELL_LENGTH
        # In a height H (parts of) up to (H/object_height)+1 objects may live side-by-side.
        # True, in the case where the camera is "synchronized" with the game world it will be
        # (H/object_height), but usually there are parts of objects at top and bottom.
        for y in xrange(SCREEN_Y / CELL_LENGTH + 1):
            for x in xrange(SCREEN_X / CELL_LENGTH + 1):
                # coordinates of this cell in gol_state
                gol_x, gol_y = gol_x0 + x, gol_y0 + y
                
                if gol_state[gol_x, gol_y]:
                    # screen coordinates of this cell with this camera
                    cell_y = -(camera_y % CELL_LENGTH) + CELL_LENGTH * y
                    cell_x = -(camera_x % CELL_LENGTH) + CELL_LENGTH * x
                    rect = pygame.Rect((cell_x, cell_y), (CELL_LENGTH, CELL_LENGTH))
                    screen.fill(BLACK, rect)
        
        
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
