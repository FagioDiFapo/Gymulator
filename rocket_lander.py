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

class Polygon:
    DEFAULT_COLOR = (255, 255, 255)

    def __init__(self, vertices = [[-1,1],[1,1],[1,-1],[-1,-1]], color = DEFAULT_COLOR):
        self.vertices = vertices
        self.color = color

    def transform(self, resolution, displacement, rotation, vertex):
        x = vertex[0]
        y = vertex[1]
        [x, y] = [x*resolution, y*resolution]
        [x, y] = [x*math.cos(rotation)-y*math.sin(rotation), x*math.sin(rotation)+y*math.cos(rotation)]
        [x, y] = [displacement[0]*resolution+x, displacement[1]*resolution+y]
        return [x, y]

    def create_transform(self, resolution, displacement, rotation):
        def adapted_transform(vertex):
            return self.transform(resolution, displacement, rotation, vertex)
        return adapted_transform


    def draw(self, display, resolution, displacement, rotation):
        transform_function = self.create_transform(resolution, displacement, rotation)
        pygame.draw.polygon(display, self.color, list(map(transform_function, self.vertices)))

class Rocket():
    position = (0., 0.)
    rotation = 0.

    thruster_angle = math.pi/2

    def __bell_transform(self, vertex):
        x = vertex[0]
        y = vertex[1]
        angle = self.thruster_angle
        [x, y] = [x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle) + y*math.cos(angle)]
        [x, y] = [x, y-self.body_height/2]
        return [x, y]

    def __init__(self, width, height):
        hwidth = width/2
        hheight = height/2
        self.body_height = height
        self.body_vertices = [[-hwidth,hheight],[hwidth,hheight],[hwidth,-hheight],[-hwidth,-hheight]]
        self.bell_vertices = [[-hwidth/2,hwidth],[hwidth/2,hwidth],[hwidth,-hwidth],[-hwidth,-hwidth]]
        self.body = Polygon(self.body_vertices)
        self.bell = Polygon(list(map(self.__bell_transform,self.bell_vertices)), (50, 50, 50))

    def draw(self, display, resolution):
        self.bell.vertices = list(map(self.__bell_transform,self.bell_vertices))
        self.bell.draw(display, resolution, self.position, self.rotation)
        self.body.draw(display, resolution, self.position, self.rotation)



class RocketLander(gym.Env):

    BACKGROUND_COLOR = (100, 100, 150)
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 800
    RESOLUTION = 10 #in pixels per meter

    running = True
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    things = []

    def __init__(self):
        self.things.append(Rocket(3.7,47.7))
        self.things[0].position = (20, 20)
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
            self.things[0].position = (10 + 20+10*math.sin(float(pygame.time.get_ticks())/1000), 30)
            self.things[0].rotation = float(pygame.time.get_ticks())/1000
            self.things[0].thruster_angle = math.pi/18*math.sin(float(pygame.time.get_ticks())/1000)
            # render
            self.screen.fill(self.BACKGROUND_COLOR)
            #pygame.draw.circle(self.screen, (255, 255, 255), (20, 20), 20)
            for thing in self.things: thing.draw(self.screen, self.RESOLUTION)
            pygame.display.update()
            self.clock.tick(60)
        pygame.quit()

lander = RocketLander()
lander.run()