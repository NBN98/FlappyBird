import pygame
import neat
import time
import os
import random
pygame.font.init()

"""
get_mask is for perfect pixel collision:
instead of box collision, we define masks which analyze the pixel of a image within a box. ==> Compare different pixels
within those boxes to avoid collision

"""

"""
For Neat algorithm:
Breed best bird from 1 population, mutate them and again and again
Input: Bird Y, Top pipe, Bottom Pipe (one should be enoúgh, but both are better)
Output: Just 1 Neuron for jumo/or not
Activation function: TanH
Population size: #of birds at each generation ==> starting at 100
Gen 0: 100
Gen 1: 100 (better)
Fitness Function: longest distance is the best bird
Max Generations: 30 
"""
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 620
GEN = 0

#scales the loaded images 2x // loaded in a sequential lists (all 3 animations)
BIRD_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "pipe.png")))
#BACKGROUND_IMG = pygame.transform.scale(pygame.image.load(os.path.join("img", "bg.png")), (720, 620))
BACKGROUND_IMG = pygame.transform.scale(pygame.image.load(os.path.join("img", "back.png")), (600, 620))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "base.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
    #constants
    IMG = BIRD_IMG
    MAX_ROTATION = 25
    ROT_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x      #STarting positions
        self.y = y
        self.tilt = 0    #Starting tilt
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMG[0]

    def jump(self):
        self.velocity = -10.5   #negative bc upwards
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.velocity*self.tick_count + 1.5*self.tick_count**2  #moving pixels

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        #adapting the tilt movement when moving upwards
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VELOCITY

    def draw(self, win):
        self.img_count += 1
        #flipping animation movement
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMG[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMG[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMG[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMG[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMG[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMG[1]
            self.img_count = self.ANIMATION_TIME*2

        #rotate image around center // credits to stackoverflow
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VELO = 10

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100  #100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #top pipe
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 400) #50 #450
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELO

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        
        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset) #returns None
        top_point = bird_mask.overlap(top_mask, top_offset) #returns None

        if bottom_point or top_point:
            return True

        return False

class Base:
    VELO = 10
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELO    #move to the left, thats why "-"
        self.x2 -= self.VELO

        #Base image will append at the end every time
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH    

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BACKGROUND_IMG, (0,0))     #topleft (0,0)
    #win.blit(BASE_IMG, (0, 400))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Generation: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))




    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []

    birds = []

    for _, g in genomes:    #genomes take tuples
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)


    base = Base(550)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        #bird.move()
        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        remove = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1      #every bird hits pipe --> remove
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:     #check if we passed the pipe, to generate new pipe
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)

           

            pipe.move()

        if add_pipe:
            score = score + 1
            for g in ge:
                g.fitness += 5       #add fitness/reward every time its passed pipe
            pipes.append(Pipe(700))

        for r in remove:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 550 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
            
        base.move()
        draw_window(win, birds, pipes, base, score, GEN)
    



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, 
        neat.DefaultStagnation, config_path) #from txt file

    population = neat.Population(config)

    #giving stats
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main,100)        #100 generations

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

