from pygame import gfxdraw
import numpy
import gym
import Box2D
from Box2D.b2 import (
    circleShape,
    contactListener,
    edgeShape,
    fixtureDef,
    polygonShape,
    revoluteJointDef,
)

import pygame
import math
from sys import exit

class Thing:
        DEFAULT_COLOR = (255, 255, 255)
        position = (0, 0)
        rotation = 0
        def __init__(self, vertices = [(-1,1),(1,1),(1,-1),(-1,-1)], color = DEFAULT_COLOR):
            self.vertices = vertices
            self.color = color

        def transform(self, position, resolution):
            x = position[0]
            y = position[1]
            (x, y) = (x*resolution, y*resolution)
            (x, y) = (x*math.cos(self.rotation)-y*math.sin(self.rotation), x*math.sin(self.rotation) + y*math.cos(self.rotation))
            (x, y) = (self.position[0]+x, self.position[1]+y)
            return (x, y)

        def create_transform(self, resolution):
            def transform_with_scale(position):
                return self.transform(position, resolution)
            return transform_with_scale


        def draw(self, display, resolution):
            transform_function = self.create_transform(resolution)
            pygame.draw.polygon(display, self.color, list(map(transform_function, self.vertices)))

class RocketLander(gym.Env):

    BACKGROUND_COLOR = (0, 0, 0)
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 400
    RESOLUTION = 100 #in pixels per meter

    running = True
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    things = []

    def __init__(self):
        self.things.append(Thing())
        self.things[0].position = (200, 200)
        self.things[0].rotation = math.pi/4

    def run(self):
        pygame.init()
        while self.running:
            # inputs
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        self.running = False

            # logic
            self.things[0].position = (200+100*math.sin(float(pygame.time.get_ticks())/1000), 200)
            self.things[0].rotation = float(pygame.time.get_ticks())/1000
            # render
            self.screen.fill(self.BACKGROUND_COLOR)
            #pygame.draw.circle(self.screen, (255, 255, 255), (20, 20), 20)
            for thing in self.things: thing.draw(self.screen, self.RESOLUTION)
            pygame.display.update()
            self.clock.tick(60)
        pygame.quit()

lander = RocketLander()
lander.run()