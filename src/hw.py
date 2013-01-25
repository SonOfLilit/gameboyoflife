import sys, pygame, time
#from pygame.locales import *


black = 0, 0, 0
class game(object):
    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print "QUIT"
                return 0
            elif event.type == pygame.KEYDOWN:
                #self.go = True
                direction=event.key
                print "got_down"
                if direction == pygame.K_UP:
                    self.speed[1] = 5
                    self.speed[0] = 0
                elif direction == pygame.K_DOWN:
                    self.speed[1] = -5
                    self.speed[0] = 0
                elif direction == pygame.K_LEFT:
                    self.speed[0] = 5
                    self.speed[1] = 0
                elif direction == pygame.K_RIGHT:
                    self.speed[0] = -5
                    self.speed[1] = 0
            elif event.type == pygame.KEYUP:
                print "got_up"
                self.speed[0] = 0
                self.speed[1] = 0

    def doi(self, i):
        #if not self.go:
            #return
        for r in xrange(i):
            self.do()
        #self.go = False

    def do(self):
#        for event in pygame.event.get():
 #           if event.type == pygame.QUIT:
  #              print "QUIT"
   #             return 0
        #time.sleep(1)
        self.ballrect = self.ballrect.move(self.speed)
        if self.ballrect.left < 0 or self.ballrect.right > self.width:
            self.speed[0] = -self.speed[0]
        if self.ballrect.top < 0 or self.ballrect.bottom > self.height:
            self.speed[1] = -self.speed[1]

        self.screen.fill(black)
        self.screen.blit(self.ball, self.ballrect)
        pygame.display.flip()

            
    def __init__(self):
        #self.go = False
        pygame.quit()
        pygame.init()
        self.size = self.width, self.height = 640, 240
        self.speed = [2, 2]
        self.screen = pygame.display.set_mode(self.size)

        self.ball = pygame.image.load("ball.gif")
        self.ballrect = self.ball.get_rect()
        self.screen.fill(black)
        self.screen.blit(self.ball, self.ballrect)
        pygame.display.flip()

print __name__
