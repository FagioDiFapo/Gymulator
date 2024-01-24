import gym
import pymunk
import pygame
import math

class Polygon:
    DEFAULT_COLOR = (255, 255, 255)

    def __init__(self, vertices = [[-1,1],[1,1],[1,-1],[-1,-1]], color = DEFAULT_COLOR):
        self.vertices = vertices
        self.color = color

    def transform(self, resolution, displacement, rotation, vertex):
        x = vertex[0]
        y = -vertex[1]
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
    #position = (0., 0.)
    #angle = 0.
    #mass = 25600

    width = 3.7
    height = 47.7

    thruster_angle = 0.
    thruster_power = 1.
    legs_angle = math.pi/4

    def __bell_transform(self, vertex):
        x = vertex[0]
        y = vertex[1]
        angle = self.thruster_angle
        [x, y] = [x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle) + y*math.cos(angle)]
        [x, y] = [x, y-self.height/2]
        return [x, y]

    def __exhaust_transform(self, vertex):
        x = vertex[0]
        y = vertex[1]
        [x, y] = [self.thruster_power*x, self.thruster_power*y]
        [x, y] = self.__bell_transform([x, y])
        return [x, y]

    def __leg_transform(self, vertex, left):
        factor = -1 if left else 1
        x = vertex[0]
        y = vertex[1]
        angle = self.legs_angle
        [x, y] = [x*math.cos(factor*angle)-y*math.sin(factor*angle), x*math.sin(factor*angle) + y*math.cos(factor*angle)]
        [x, y] = [x, y]
        [x, y] = [x+self.width*factor/2, y-self.height/2]
        return [x,y]


    def __init__(self, space):
        # VISUAL REPRESENTATION
        hwidth = self.width/2
        hheight = self.height/2
        self.booster_vertices = [[-hwidth,hheight],[hwidth,hheight],[hwidth,-hheight],[-hwidth,-hheight]]
        self.bell_vertices = [[-hwidth/2,hwidth],[hwidth/2,hwidth],[hwidth,-hwidth],[-hwidth,-hwidth]]
        self.exhaust_vertices = [[0,hwidth/2],[hwidth/2,-hwidth],[0,-4*hwidth],[-hwidth/2,-hwidth]]
        self.leg_vertices = [[-hwidth/5, 0],[hwidth/5, 0],[hwidth/10, -self.width],[-hwidth/10, -self.width]]
        self.booster = Polygon(self.booster_vertices)
        self.bell = Polygon([self.__bell_transform(vertex) for vertex in self.bell_vertices], (50, 50, 50))
        self.leg_l = Polygon([self.__leg_transform(vertex, True) for vertex in self.leg_vertices], (50, 50, 50))
        self.leg_r = Polygon([self.__leg_transform(vertex, False) for vertex in self.leg_vertices], (50, 50, 50))
        self.exhaust = Polygon([self.__exhaust_transform(vertex) for vertex in self.exhaust_vertices], (255, 255, 50))
        #self.bell = Polygon(list(map(self.__bell_transform,self.bell_vertices)), (50, 50, 50))

        # PYSICAL SIMULATION
        body = pymunk.Body()
        body.position = 50,0
        self.body = body
        body_poly = pymunk.Poly(self.body, self.booster_vertices)
        body_poly.mass = 25600
        leg_poly_l = pymunk.Poly(self.body, [self.__leg_transform(vertex, True) for vertex in self.leg_vertices])
        leg_poly_l.mass = 0
        leg_poly_r = pymunk.Poly(self.body, [self.__leg_transform(vertex, False) for vertex in self.leg_vertices])
        leg_poly_r.mass = 0

        space.add(body, body_poly)
        space.add(leg_poly_l, leg_poly_r)


    def draw(self, display, resolution):
        self.exhaust.vertices = [self.__exhaust_transform(vertex) for vertex in self.exhaust_vertices]
        self.exhaust.draw(display, resolution, self.body.position, self.body.angle)
        self.bell.vertices = [self.__bell_transform(vertex) for vertex in self.bell_vertices]
        self.bell.draw(display, resolution, self.body.position, self.body.angle)
        self.leg_l.draw(display, resolution, self.body.position, self.body.angle)
        self.leg_r.draw(display, resolution, self.body.position, self.body.angle)
        self.booster.draw(display, resolution, self.body.position, self.body.angle)

class Planet():
    def __init__(self, space):
        # VISUAL REPRESENTATION
        #hwidth = self.width/2
        #hheight = self.height/2
        #self.booster_vertices = [[-hwidth,hheight],[hwidth,hheight],[hwidth,-hheight],[-hwidth,-hheight]]
        #self.bell_vertices = [[-hwidth/2,hwidth],[hwidth/2,hwidth],[hwidth,-hwidth],[-hwidth,-hwidth]]
        #self.exhaust_vertices = [[0,hwidth/2],[hwidth/2,-hwidth],[0,-4*hwidth],[-hwidth/2,-hwidth]]
        #self.booster = Polygon(self.booster_vertices)
        #self.bell = Polygon([self.__bell_transform(vertex) for vertex in self.bell_vertices], (50, 50, 50))
        #self.exhaust = Polygon([self.__exhaust_transform(vertex) for vertex in self.exhaust_vertices], (255, 255, 50))

        self.body = pymunk.Body(1,100,body_type= pymunk.Body.STATIC)
        self.body.position = 60,60
        self.terrain_vertices = [(-50,5),(50,5),(50,-5),(-50,-5)]
        self.terrain = Polygon(self.terrain_vertices)
        shape = pymunk.Poly(self.body,self.terrain_vertices)
        space.add(self.body,shape)

    def draw(self, display, resolution):
        self.terrain.draw(display, resolution, self.body.position, self.body.angle)

class RocketLander(gym.Env):

    # RENDERING
    BACKGROUND_COLOR = (100, 100, 150)
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 800
    RESOLUTION = 10 #in pixels per meter

    running = True
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    things = []
    space = pymunk.Space()
    space.gravity = 0,9.81

    def __init__(self):

        self.things.append(Rocket(self.space))
        self.things.append(Planet(self.space))
        #self.things[0].position = (20, 20)
        #self.things[0].rotation = math.pi/4


    def run(self):
        pygame.init()
        while self.running:
            # inputs
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        self.running = False

            # logic
            dt = self.clock.tick(60)/1000
            self.space.step(dt)
            self.things[0].thruster_angle = math.pi/18*math.sin(float(pygame.time.get_ticks())/1000)
            self.things[0].thruster_power = 0.5+0.5*math.sin(float(pygame.time.get_ticks())/1000)
            # render
            self.screen.fill(self.BACKGROUND_COLOR)
            #pygame.draw.circle(self.screen, (255, 255, 255), (20, 20), 20)
            for thing in self.things:
                thing.draw(self.screen, self.RESOLUTION)
            pygame.display.update()
        pygame.quit()

lander = RocketLander()
lander.run()