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
class Cell(pygame.sprite.Sprite):
    _ALL_CELLS = {}
    def __init__(self, x, y, color):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([CELL_LENGTH, CELL_LENGTH])
        
        self.rect = self.image.get_rect()
        self.rect.x = x * CELL_LENGTH
        self.rect.y = y * CELL_LENGTH

        self.set_color(color)

    def set_color(self, color):
        if color:
            fill_color = BLACK
        else:
            fill_color = WHITE
        self.image.fill(fill_color)

class Character(pygame.sprite.Sprite):
    # Dir: X, Y
    DIRECTIONS = {"UP":(0,2),
                  "DOWN":(0,-2),
                  "LEFT":(-2, 0),
                  "RIGHT":(2, 0)}
    def __init__(self, x, y, speed=(0, 0), acc=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface([CELL_LENGTH, CELL_LENGTH])
        
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * CELL_LENGTH, y * CELL_LENGTH
        self.image.fill(BLUE)
        self.speed = speed
        self.acc = acc

    def Tick(self):
        self.speed = (self.speed[0] + self.acc[0], self.speed[1] + self.acc[1])
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        print "x:" , self.rect.x
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


GOL_TICK = pygame.USEREVENT + 0

# This dir is for key pressess which should affect direction.
# Use diffn't dir for other functions.
PYGAME_KEY_TO_DIR = {pygame.K_LEFT : "LEFT",
                     pygame.K_RIGHT : "RIGHT"}

# TODO: Utilze this?
PYGAME_KEY_TO_FUNC = {pygame.K_p : "PAUSEKEY"}

def go():
    screen = pygame.display.set_mode([640, 480])
    clock = pygame.time.Clock()
    sprites = pygame.sprite.Group()

    gol_state = numpy.zeros((80, 80))
    x, y = glider_round1.shape
    gol_state[:x, :y] = glider_round1
    character = Character(50, 50)
    sprites.add(character)
    
    cells_dict = {}
    for y in xrange(1, gol_state.shape[0] - 1):
        for x in xrange(1, gol_state.shape[1] - 1):
            cell = Cell(x, y, gol_state[x][y])
            cells_dict[(x, y)] = cell
            sprites.add(cell)

    pygame.time.set_timer(GOL_TICK, 1000)

    done, pause = False, False
    while not done:
        if pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    pause = not pause
            continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == GOL_TICK:
                gol_state = gol_round(gol_state)
                for y in xrange(1, gol_state.shape[0] - 1):
                    for x in xrange(1, gol_state.shape[1] - 1):
                        cells_dict[(x, y)].set_color(gol_state[x][y])
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
        sprites.draw(screen)
        clock.tick(20)
        pygame.display.flip()

def main():
    try:
        pygame.init()
        go()
    finally:
        pygame.quit()
    
print "HWAT"
if __name__ == "__main__":
    main()
