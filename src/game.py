import random
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

def main():
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_X, SCREEN_Y])
    clock = pygame.time.Clock()

    gol_state = numpy.zeros((800, 800))
    x, y = glider_round1.shape
    gol_state[:x, :y] = glider_round1
    print gol_state.shape

    camera_x, camera_y = 0, 0
    
    pygame.time.set_timer(GOL_TICK, 400)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == GOL_TICK:
                gol_state = gol_round(gol_state)

        screen.fill(BLUE)
        
        gol_x0 = camera_x / CELL_LENGTH
        gol_y0 = camera_y / CELL_LENGTH
        for y in xrange(SCREEN_Y / CELL_LENGTH + 1):
            for x in xrange(SCREEN_X / CELL_LENGTH + 1):
                gol_x, gol_y = gol_x0 + x, gol_y0 + y
                if gol_state[gol_x, gol_y]:
                    cell_y = -(camera_y % CELL_LENGTH) + CELL_LENGTH * y
                    cell_x = -(camera_x % CELL_LENGTH) + CELL_LENGTH * x
                    rect = pygame.Rect((cell_x, cell_y), (CELL_LENGTH, CELL_LENGTH))
                    screen.fill(BLACK, rect)
#                    screen.blit(CELL_IMAGE, (cell_x, cell_y))
        
        camera_x -= 1
        camera_y -= 0

        clock.tick(20)
        pygame.display.flip()
        

    pygame.quit()
    

if __name__ == "__main__":
    main()
