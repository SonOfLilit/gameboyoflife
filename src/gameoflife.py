# Copyright 2013 Aur Saraf and friends.


import numpy

SIDES = numpy.array([1,0, 1])
SUM_3 = numpy.array([1, 1, 1])
def round(initial):
    # If you struggle to understand this algorithm, blame copyright laws
    neighbours = numpy.zeros(initial.shape, dtype=int)
    for i in xrange(1, len(initial) - 1):
        neighbours[i] += numpy.convolve(initial[i], SIDES)[1:-1]
        sum_3 = numpy.convolve(initial[i], SUM_3)[1:-1]
        neighbours[i - 1] += sum_3
        neighbours[i + 1] += sum_3
    # zero the edges
    neighbours[0,: ] = 0
    neighbours[-1,: ] = 0
    neighbours[:, 0] = 0
    neighbours[:, -1] = 0
    surviving = ((initial == 1) & (neighbours > 1) & (neighbours < 4))
    # a new cell forms if a square has exactly three members
    newborn = ((initial == 0) & (neighbours == 3))
    return (surviving | newborn).astype(int)
    
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
