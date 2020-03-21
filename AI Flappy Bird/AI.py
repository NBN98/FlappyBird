import pygame
import neat
import time
import os
import random

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 620

#scales the loaded images 2x // loaded in a sequential lists (all 3 animations)
BIRD_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "pipe.png")))
#BACKGROUND_IMG = pygame.transform.scale(pygame.image.load(os.path.join("img", "bg.png")), (720, 620))
BACKGROUND_IMG = pygame.transform.scale(pygame.image.load(os.path.join("img", "bg.png")), (600, 620))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "base.png")))



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

def draw_window(win, bird):
    win.blit(BACKGROUND_IMG, (0,0))     #topleft (0,0)
    #win.blit(BASE_IMG, (0, 400))
    bird.draw(win)
    pygame.display.update()

def main():
    bird = Bird(200, 200)
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        bird.move()
        draw_window(win, bird)
    pygame.quit()
    quit()

main()