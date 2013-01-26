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
    DSPEED = 1000
    DIRECTIONS = {"LEFT":{"x":-DSPEED, "y":0},
          "RIGHT":{"x":DSPEED, "y":0}}
    G = 1

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([CELL_LENGTH, CELL_LENGTH]) 
        self.image.fill(RED)
       
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * CELL_LENGTH, y * CELL_LENGTH
        self.x = self.rect.x
        self.y = self.rect.y
        self.speed = {"x": None, "y": None}

    def Tick(self):
        if self.speed["x"]:
            self.x += self.speed["x"]
        if self.speed["y"] != None:
            self.y += self.speed["y"]
            self.speed["y"] += Character.G
        print self.speed

    def MoveInDirection(self, direction):
        if not direction:
            return
        
        if direction == "LEFT":
            self.speed["x"] = -Character.DSPEED
        elif direction == "RIGHT":
            self.speed["x"] = Character.DSPEED
        elif direction == "SPACE" and self.speed["y"] == None:
            self.speed["y"] = -Character.DSPEED

    def StopMovement(self):
        self.speed["x"] = None

    def StopFalling(self):
        self.speed["y"] = None

    def IsDead(self):
        # TODO: DECIDE.
        return (self.speed > -10 or
                self.cell_y < -100)

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
    x, y = glider_round1.shape
    gol_state[:x, :y] = glider_round1
    gol_state[4:6, 10:12] = 1
    gol_state[10:13, 17:19] = 1

    sprites = pygame.sprite.Group()
    character = Character(10, 10)
    sprites.add(character)

    camera_x, camera_y = 0, 0
    
    done = False
    pygame.time.set_timer(GOL_TICK, 400)
    pygame.time.set_timer(PLAYER_TICK, 50)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == GOL_TICK:
                gol_state = gol_round(gol_state)
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

        screen.fill(BLUE)
        
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
        
        sprites.draw(screen)

        camera_x -= 0
        camera_y -= 0

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
