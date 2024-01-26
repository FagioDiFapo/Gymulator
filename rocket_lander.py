import gym
import pymunk
import pygame
import math

class Camera:

    def __init__(self, position, resolution, scale):
        self.position = position
        self.resolution = resolution
        self.scale = scale

class Shape:
    def __init__(self, vertices = [[-1,1],[1,1],[1,-1],[-1,-1]], color = (255, 255, 255)):
        self.vertices = vertices
        self.color = color

    def __transform(self, camera, displacement, rotation, vertex):
        x = vertex[0]
        y = vertex[1]
        [x, y] = [x*math.cos(rotation)-y*math.sin(rotation), x*math.sin(rotation)+y*math.cos(rotation)]
        [x, y] = [x+displacement[0], y+displacement[1]]
        [x, y] = [camera.scale*(x-camera.position[0])+camera.resolution[0]/2, camera.scale*(y-camera.position[1])+camera.resolution[1]/2]
        return [x, y]

    def draw(self, display, camera, displacement, rotation):
        pygame.draw.polygon(display, self.color, [self.__transform(camera, displacement, rotation, vertex) for vertex in self.vertices])

class Circle(Shape):
    def __init__(self, radius = 1, color = (255, 255, 255), line_color = (255, 0, 0)):
            self.radius = radius
            self.color = color
            self.line_color = line_color

    def draw(self, display, camera, displacement, rotation):
        pygame.draw.circle(display, self.color, self._Shape__transform(camera, displacement, rotation, [0, 0]), self.radius*camera.scale)
        pygame.draw.line(display, self.line_color, self._Shape__transform(camera, displacement, rotation, [0, 0]), self._Shape__transform(camera, displacement, rotation, [0, -self.radius]), width = 3)


class Rocket(pymunk.Body):

    # PARAMETERS
    width = 3.7 #m
    height = 47.7 #m
    empty_mass = 25600 #Kg
    legs_angle = math.pi/4 #Rad
    thruster_angle = math.pi/18 #Rad
    thruster_force = 845000 #Newtons

    attitude_indicator_size = 10 #Pixels

    # VARIABLES
    thruster_vector = 0. #[-1 1]
    thruster_power = 0. #[0 1]

    def __bell_transform(self, vertex):
        x = vertex[0]
        y = vertex[1]
        angle = self.thruster_angle*self.thruster_vector
        [x, y] = [x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle) + y*math.cos(angle)]
        [x, y] = [x, y+self.height/2]
        return [x, y]

    def __exhaust_transform(self, vertex):
        x = vertex[0]
        y = vertex[1]
        [x, y] = [self.thruster_power*x, self.thruster_power*y]
        [x, y] = self.__bell_transform([x, y])
        return [x, y]

    def __leg_transform(self, vertex, left):
        factor = 1 if left else -1
        x = vertex[0]
        y = vertex[1]
        angle = self.legs_angle
        [x, y] = [x*math.cos(factor*angle)-y*math.sin(factor*angle), x*math.sin(factor*angle) + y*math.cos(factor*angle)]
        [x, y] = [x, y]
        [x, y] = [x-self.width*factor/2, y+self.height/2]
        return [x, y]

    def __attitude_indicator_transform(self, vertex, scale):
        x = vertex[0]
        y = vertex[1]
        indicator_size = self.attitude_indicator_size
        [x, y] = [indicator_size*x/scale, indicator_size*y/scale]
        return [x, y]

    def __init__(self, space):
        # VERTICES
        hwidth = self.width/2
        hheight = self.height/2
        booster_vertices = [[-hwidth,-hheight],[hwidth,-hheight],[hwidth,hheight],[-hwidth,hheight]]
        leg_vertices = [[-hwidth/5, 0],[hwidth/5, 0],[hwidth/10, self.width],[-hwidth/10, self.width]]
        self.bell_vertices = [[-hwidth/3,-hwidth],[hwidth/3,-hwidth],[self.width/3,hwidth],[-self.width/3,hwidth]]
        self.exhaust_vertices = [[0,-hwidth/2],[hwidth/2,hwidth],[0,4*hwidth],[-hwidth/2,hwidth]]
        self.attitude_indicator_vertices = [[0,-1],[1,1],[-1,1]]

        # VISUAL REPRESENTATION
        #static elements
        self.booster = Shape(booster_vertices)
        self.leg_l = Shape([self.__leg_transform(vertex, True) for vertex in leg_vertices], (50, 50, 50))
        self.leg_r = Shape([self.__leg_transform(vertex, False) for vertex in leg_vertices], (50, 50, 50))
        #dynamic elements
        self.bell = Shape([self.__bell_transform(vertex) for vertex in self.bell_vertices], (50, 50, 50))
        self.exhaust = Shape([self.__exhaust_transform(vertex) for vertex in self.exhaust_vertices], (255, 255, 50))
        self.attitude_indicator = Shape([self.__attitude_indicator_transform(vertex, 10) for vertex in self.attitude_indicator_vertices], (255, 50, 50))

        # PYSICAL REPRESENTATION
        super().__init__()
        self.position = [0,-50]
        body_poly = pymunk.Poly(self, self.booster.vertices)
        leg_poly_l = pymunk.Poly(self, self.leg_l.vertices)
        leg_poly_r = pymunk.Poly(self, self.leg_r.vertices)
        body_poly.mass = self.empty_mass
        body_poly.friction = 0.6
        leg_poly_l.friction = 0.6
        leg_poly_r.friction = 0.6

        space.add(self, body_poly, leg_poly_l, leg_poly_r)

    def thrust(self):
        angle = self.thruster_angle*self.thruster_vector
        [x, y] = [0, -self.thruster_force*self.thruster_power]
        [x, y] = [x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle) + y*math.cos(angle)]
        self.apply_force_at_local_point([x, y], [0, self.height/2])

    def draw(self, display, camera):
        self.attitude_indicator.vertices = [self.__attitude_indicator_transform(vertex, camera.scale) for vertex in self.attitude_indicator_vertices]
        self.exhaust.vertices = [self.__exhaust_transform(vertex) for vertex in self.exhaust_vertices]
        self.bell.vertices = [self.__bell_transform(vertex) for vertex in self.bell_vertices]

        self.attitude_indicator.draw(display, camera, self.position, self.angle)
        self.exhaust.draw(display, camera, self.position, self.angle)
        self.bell.draw(display, camera, self.position, self.angle)
        self.leg_l.draw(display, camera, self.position, self.angle)
        self.leg_r.draw(display, camera, self.position, self.angle)
        self.booster.draw(display, camera, self.position, self.angle)

class Planet(pymunk.Body):
    pad_width = 86 #m
    pad_height = 10 #m
    terrain_width = 100000 #m
    terrain_height = 100000 #m
    diameter = 12742000 #m

    def __init__(self, space):
        hwidth = self.pad_width/2
        hheight = self.pad_height/2
        htwidth = self.terrain_width/2
        pad_vertices = [(-hwidth,hheight),(hwidth,hheight),(hwidth,-hheight),(-hwidth,-hheight)]
        terrain_vertices = [(-htwidth,hheight),(htwidth,hheight),(htwidth,self.terrain_height+hheight),(-htwidth,self.terrain_height+hheight)]
        # PYSICAL REPRESENTATION
        super().__init__(body_type= pymunk.Body.STATIC)
        self.position = [0,-hheight]
        pad_poly = pymunk.Poly(self,pad_vertices)
        terrain_poly = pymunk.Poly(self, terrain_vertices)
        pad_poly.friction = 0.6
        terrain_poly.friction = 0.6
        space.add(self, pad_poly, terrain_poly)
        # VISUAL REPRESENTATION
        self.pad = Shape(pad_vertices)
        self.terrain = Shape(terrain_vertices, (25, 25, 25))
        #self.terrain = Circle(self.diameter/2, color = (100, 150, 255), line_color = (255, 0, 0))

    def draw(self, display, camera):
        self.pad.draw(display, camera, self.position, self.angle)
        self.terrain.draw(display, camera, self.position, self.angle)
        #self.terrain.draw(display, camera, [self.position[0], self.position[1]+self.pad_height/2], self.angle)

class RocketLander(gym.Env):

    # RENDERING
    BACKGROUND_COLOR = (100, 100, 150)
    WINDOW_RESOLUTION = [1000, 800]
    RENDER_SCALE = 10 #in pixels per meter

    running = True
    screen = pygame.display.set_mode(WINDOW_RESOLUTION)
    clock = pygame.time.Clock()

    things = []
    space = pymunk.Space()
    space.gravity = [0,9.81]

    # USER INPUTS
    a_down = False
    d_down = False
    w_down = False

    def __init__(self):
        self.camera = Camera([10, 10], self.WINDOW_RESOLUTION, self.RENDER_SCALE)
        self.rocket = Rocket(self.space)
        self.planet = Planet(self.space)

    def handle_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.MOUSEWHEEL:
                    self.camera.scale *= 1.1 if event.y > 0 else 0.9
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_a:
                            self.a_down = True
                        case pygame.K_d:
                            self.d_down = True
                        case pygame.K_w:
                            self.w_down = True
                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_a:
                            self.a_down = False
                        case pygame.K_d:
                            self.d_down = False
                        case pygame.K_w:
                            self.w_down = False

    def handle_logic(self):
        dt = self.clock.tick(60)/1000
        self.camera.position = self.rocket.position
        self.rocket.thruster_power = float(self.w_down)
        self.rocket.thruster_vector = float(self.a_down) - float(self.d_down)
        self.rocket.thrust()

        self.space.step(dt)

    def render(self):
        self.screen.fill(self.BACKGROUND_COLOR)
        self.rocket.draw(self.screen, self.camera)
        self.planet.draw(self.screen, self.camera)
        pygame.display.update()


    def run(self):
        pygame.init()
        while self.running:
            # inputs
            self.handle_events()
            # logic
            self.handle_logic()
            # render
            self.render()
        pygame.quit()

lander = RocketLander()
lander.run()