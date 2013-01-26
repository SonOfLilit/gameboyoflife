import numpy

def round(Z):
    """
    From http://dana.loria.fr/doc/game-of-life.html
    """
    # find number of neighbours that each square has
    N = numpy.zeros(Z.shape, dtype=int)
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
assert (round(glider_round1) == glider_round2).all()
# test that outer edges remain zero
glider = glider_round1
for i in xrange(20):
    glider = round(glider)
square = numpy.array(
    [[0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0],
     [0, 0, 0, 1, 1, 0],
     [0, 0, 0, 1, 1, 0],
     [0, 0, 0, 0, 0, 0]])
assert (glider == square).all()
