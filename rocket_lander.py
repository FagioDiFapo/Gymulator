import gymnasium as gym
import pymunk
import pygame
import numpy as np
import math
import random as rand


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
        [x, y] = vertex
        [x, y] = [x*math.cos(rotation)-y*math.sin(rotation), x*math.sin(rotation)+y*math.cos(rotation)]
        [x, y] = [x+displacement[0], y+displacement[1]]
        [x, y] = [camera.scale*(x-camera.position[0])+camera.resolution[0]/2, camera.scale*(y-camera.position[1])+camera.resolution[1]/2]
        return [x, y]

    def draw(self, display, camera, displacement, rotation):
        pygame.draw.polygon(display, self.color, [self.__transform(camera, displacement, rotation, vertex) for vertex in self.vertices])


class Circle(Shape):

    DEBUG_LINE_WIDTH = 3 #pixels

    def __init__(self, radius = 1, color = (255, 255, 255), line_color = (255, 0, 0)):
        self.radius = radius
        self.color = color
        self.line_color = line_color

    def draw(self, display, camera, displacement, rotation):
        pygame.draw.circle(display, self.color, self._Shape__transform(camera, displacement, rotation, [0, 0]), self.radius*camera.scale)
        pygame.draw.line(display, self.line_color,
                self._Shape__transform(camera, displacement, rotation, [0, 0]), self._Shape__transform(camera, displacement, rotation,[0, -self.radius]),
                width = self.DEBUG_LINE_WIDTH)


class Rocket(pymunk.Body):

    # PARAMETERS
    # physycal attributes
    WIDTH = 3.7 #m
    HEIGHT = 47.7 #m
    EMPTY_MASS = 25600 #Kg
    LEGS_ANGLE = math.pi/4 #Rad
    MAX_THRUSTER_ANGLE = math.pi/18 #Rad
    MAX_THRUSTER_FORCE = 845000 #Newtons

    # visual attributes
    ATTITUDE_INDICATOR_SCALE = 10 #Pixels

    def __bell_transform(self, vertex):
        angle = self.MAX_THRUSTER_ANGLE*self.thruster_vector
        [x, y] = vertex
        [x, y] = [x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle) + y*math.cos(angle)]
        [x, y] = [x, y+self.HEIGHT/2]
        return [x, y]

    def __exhaust_transform(self, vertex):
        [x, y] = vertex
        [x, y] = [self.thruster_power*x, self.thruster_power*y]
        [x, y] = self.__bell_transform([x, y])
        return [x, y]

    def __attitude_indicator_transform(self, vertex, scale):
        indicator_size = self.ATTITUDE_INDICATOR_SCALE
        [x, y] = vertex
        [x, y] = [indicator_size*x/scale, indicator_size*y/scale]
        return [x, y]

    def update_collisions(self):
        _bodies = [self.body_poly, self.leg_poly_l, self.leg_poly_r]
        def shape_colliding(arbiter, shape, collisions):
            if shape in arbiter.shapes:
                collisions[shape] = True
        collisions = {body: False for body in _bodies}
        self.each_arbiter(shape_colliding, _bodies[0], collisions)
        self.leg_body_l.each_arbiter(shape_colliding, _bodies[1], collisions)
        self.leg_body_r.each_arbiter(shape_colliding, _bodies[2], collisions)

        self.collisions = [collisions[body] for body in _bodies]

    def __init__(self, space):
        # RUNTIME VARIABLES
        self.thruster_vector = 0. #[-1 1]
        self.thruster_power = 0. #[0 1]
        self.collisions = [False, False, False]

        # VERTICES
        hwidth = self.WIDTH/2
        hheight = self.HEIGHT/2
        # static elements
        booster_vertices = [[-hwidth,-hheight],[hwidth,-hheight],[hwidth,hheight],[-hwidth,hheight]]
        leg_vertices = [[-hwidth/5, 0],[hwidth/5, 0],[hwidth/10, self.WIDTH],[-hwidth/10, self.WIDTH]]
        # dynamic elements
        self.bell_vertices = [[-hwidth/3,-hwidth],[hwidth/3,-hwidth],[self.WIDTH/3,hwidth],[-self.WIDTH/3,hwidth]]
        self.exhaust_vertices = [[0,-hwidth/2],[hwidth/2,hwidth],[0,4*hwidth],[-hwidth/2,hwidth]]
        self.attitude_indicator_vertices = [[0,-1],[1,1],[-1,1]]

        # VISUAL REPRESENTATION
        self.booster = Shape(booster_vertices)
        self.leg_l = Shape(leg_vertices, (50, 50, 50))
        self.leg_r = Shape(leg_vertices, (50, 50, 50))
        self.bell = Shape([self.__bell_transform(vertex) for vertex in self.bell_vertices], (50, 50, 50))
        self.exhaust = Shape([self.__exhaust_transform(vertex) for vertex in self.exhaust_vertices], (255, 255, 50))
        self.attitude_indicator = Shape([self.__attitude_indicator_transform(vertex, 10) for vertex in self.attitude_indicator_vertices], (255, 50, 50))

        # PYSICAL REPRESENTATION
        super().__init__()
        self.leg_body_l = pymunk.Body()
        self.leg_body_r = pymunk.Body()

        self.position = [0,-50]
        self.leg_body_l.position = self.position + [-hwidth, hheight]
        self.leg_body_r.position = self.position + [hwidth, hheight]
        self.body_poly = pymunk.Poly(self, self.booster.vertices)
        self.leg_poly_l = pymunk.Poly(self.leg_body_l, leg_vertices)
        self.leg_poly_r = pymunk.Poly(self.leg_body_r, self.leg_r.vertices)
        self.body_poly.mass = (1-0.16)*self.EMPTY_MASS
        self.leg_poly_l.mass = 0.08*self.EMPTY_MASS
        self.leg_poly_r.mass = 0.08*self.EMPTY_MASS
        self.body_poly.friction = 0.6
        self.leg_poly_l.friction = 0.6
        self.leg_poly_r.friction = 0.6

        # landing leg constraints
        pivot_leg_l = pymunk.constraints.PivotJoint(self, self.leg_body_l, [-hwidth, hheight], [0, 0])
        pivot_leg_r = pymunk.constraints.PivotJoint(self, self.leg_body_r, [hwidth, hheight], [0, 0])
        pivot_leg_l.collide_bodies = False
        pivot_leg_r.collide_bodies = False
        rotary_spring_leg_l =  pymunk.constraints.DampedRotarySpring(self, self.leg_body_l, -self.LEGS_ANGLE, 5000000, 50000)
        rotary_spring_leg_r =  pymunk.constraints.DampedRotarySpring(self, self.leg_body_r, self.LEGS_ANGLE, 5000000, 50000)
        rotary_limit_leg_l = pymunk.constraints.RotaryLimitJoint(self, self.leg_body_l, self.LEGS_ANGLE-math.pi/36, self.LEGS_ANGLE+math.pi/36)
        rotary_limit_leg_r = pymunk.constraints.RotaryLimitJoint(self, self.leg_body_r, -self.LEGS_ANGLE-math.pi/36, -self.LEGS_ANGLE+math.pi/36)

        space.add(self, self.body_poly)
        space.add(self.leg_body_l, self.leg_poly_l, self.leg_body_r, self.leg_poly_r)
        space.add(pivot_leg_l, pivot_leg_r, rotary_spring_leg_l, rotary_spring_leg_r, rotary_limit_leg_l, rotary_limit_leg_r)

    def thrust(self):
        angle = self.MAX_THRUSTER_ANGLE*self.thruster_vector
        [x, y] = [0, -self.MAX_THRUSTER_FORCE*self.thruster_power]
        [x, y] = [x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle) + y*math.cos(angle)]
        self.apply_force_at_local_point([x, y], [0, self.HEIGHT/2])

    def draw(self, display, camera):
        self.attitude_indicator.vertices = [self.__attitude_indicator_transform(vertex, camera.scale) for vertex in self.attitude_indicator_vertices]
        self.exhaust.vertices = [self.__exhaust_transform(vertex) for vertex in self.exhaust_vertices]
        self.bell.vertices = [self.__bell_transform(vertex) for vertex in self.bell_vertices]

        self.attitude_indicator.draw(display, camera, self.position, self.angle)
        self.exhaust.draw(display, camera, self.position, self.angle)
        self.bell.draw(display, camera, self.position, self.angle)
        self.booster.draw(display, camera, self.position, self.angle)
        self.leg_l.draw(display, camera, self.leg_body_l.position,  self.leg_body_l.angle)
        self.leg_r.draw(display, camera,  self.leg_body_r.position,  self.leg_body_r.angle)

class Planet(pymunk.Body):
    PAD_WIDTH = 86 #m
    PAD_HEIGHT = 10 #m
    TERRAIN_WIDTH = 100000 #m
    TERRAIN_HEIGHT = 100000 #m
    #DIAMETER = 12742000 #m

    def __init__(self, space):
        hwidth = self.PAD_WIDTH/2
        hheight = self.PAD_HEIGHT/2
        htwidth = self.TERRAIN_WIDTH/2

        # VERTICES
        pad_vertices = [[-hwidth,hheight],[hwidth,hheight],[hwidth,-hheight],[-hwidth,-hheight]]
        terrain_vertices = [[-htwidth,hheight],[htwidth,hheight],[htwidth,self.TERRAIN_HEIGHT+hheight],[-htwidth,self.TERRAIN_HEIGHT+hheight]]

        # PYSICAL REPRESENTATION
        super().__init__(body_type= pymunk.Body.STATIC)
        self.position = [0,-hheight]
        pad_poly = pymunk.Poly(self,pad_vertices)
        self.terrain_poly = pymunk.Poly(self, terrain_vertices)
        pad_poly.friction = 0.6
        self.terrain_poly.friction = 0.6
        space.add(self, pad_poly, self.terrain_poly)

        # VISUAL REPRESENTATION
        self.pad = Shape(pad_vertices)
        self.terrain = Shape(terrain_vertices, (25, 25, 25))
        #self.terrain = Circle(self.DIAMETER/2, color = (100, 150, 255), line_color = (255, 0, 0))

    def update_collisions(self):
        bodies_to_check = [self.terrain_poly]
        def shape_colliding(arbiter, collisions):
            for shape in collisions.keys():
                if shape in arbiter.shapes:
                    collisions[shape] = True
        collisions = {body: False for body in bodies_to_check}
        self.each_arbiter(shape_colliding, collisions)

        self.collisions = [collisions[body] for body in bodies_to_check]

    def draw(self, display, camera):
        self.pad.draw(display, camera, self.position, self.angle)
        self.terrain.draw(display, camera, self.position, self.angle)
        #self.terrain.draw(display, camera, [self.position[0], self.position[1]+self.PAD_HEIGHT/2], self.angle)

class RocketLander(gym.Env):

    # PARAMETERS
    LANDER_INSTANCES = []
    # VISUAL ATTRIBUTES
    BACKGROUND_COLOR = (100, 100, 150)
    WINDOW_RESOLUTION = [1000, 700]
    RENDER_SCALE = 2 #in pixels per meter
    camera = Camera([10, 10], WINDOW_RESOLUTION, RENDER_SCALE)
    RENDER_TOGGLE = True
    # SIMULATION SETTINGS
    FPS = 60
    COMMITMENT_TIME = 5 #amount of seconds after a landing is considered valid

    # USER INPUTS
    in_left = False
    in_right = False
    in_up = False

    def __get_spaces(self):
        low = np.array([
            # relative position from target
            -1.5,-1.5,
            # relative velocity
            -1.5,-1.5,
            # angle
            -math.pi,
            # angular velocity
            -math.pi,
            # legs in contact
            0.0,0.0,
        ]).astype(np.float32)
        high = np.array([
            # relative position from target
            1.5,1.5,
            # relative velocity
            1.5,1.5,
            # angle
            math.pi,
            # angular velocity
            math.pi,
            # legs in contact
            1.0,1.0,
        ]).astype(np.float32)
        observation_space = gym.spaces.box.Box(low, high)

        # Nothing, thrust straight, thrust left and thrust right
        action_space = gym.spaces.discrete.Discrete(4)

        return action_space, observation_space

    def __get_observations(self):
        t_pos = -self.rocket.position
        r_vel = self.rocket.velocity
        observations = [
            t_pos[0]/500, t_pos[1]/500,
            r_vel[0]/100, r_vel[1]/100,
            self.rocket.angle,
            self.rocket.angular_velocity,
            int(self.rocket.collisions[1]), int(self.rocket.collisions[2])
        ]

        return observations

    def __get_reward(self, delta_time):
        reward = 0
        t_pos = -self.rocket.position - [0,self.rocket.HEIGHT/2]
        r_vel = self.rocket.velocity
        shaping = (
            - 1000 * np.sqrt(t_pos[0]/500 * t_pos[0]/500 + t_pos[1]/500 * t_pos[1]/500)
            #- 1000 * np.sqrt(r_vel[0] * r_vel[0] + r_vel[1] * r_vel[1])
            #- 100 * abs(obs[4])
            + 10 * self.rocket.collisions[1]
            + 10 * self.rocket.collisions[2]
        )
        if self.prev_shaping is not None:
            reward = shaping - self.prev_shaping
        self.prev_shaping = shaping

        reward -= self.rocket.thruster_power * 100

        terminated = False
        velocity = np.sqrt(r_vel[0]*r_vel[0] + r_vel[1]*r_vel[1])
        if (
            self.rocket.collisions[0] or self.planet.collisions[0] or
            ((self.rocket.collisions[1] or self.rocket.collisions[2]) and velocity > 5) or
            abs(t_pos[0]) > 500 or abs(t_pos[1]) > 500
        ):
            terminated = True
            #print("womp womp")
            if self.rocket.collisions[0] or self.planet.collisions[0]:
                reward += -1000
            reward += -1000#-100*velocity
        if self.rocket.collisions[1] and self.rocket.collisions[2] and velocity < 5:
            if self.contact_time > self.COMMITMENT_TIME:
                terminated = True
                reward += +1000
                #print("yipee")
            else:
                self.contact_time += delta_time
            reward += +100#-100*velocity
        else:
            self.contact_time = 0.

        return reward, terminated

    def __init_landing_scenario(self, seed):
        rand.seed(seed)
        # SIMULATION ELEMENTS
        self.contact_time = 0.
        self.prev_shaping = None
        self.space = pymunk.Space()
        self.space.gravity = [0,9.81]
        self.planet = Planet(self.space)
        self.rocket = Rocket(self.space)
        self.rocket.position = [rand.uniform(-100., 100.), rand.uniform(-200., -100.)]
        self.rocket.leg_body_l.position = self.rocket.position + [-self.rocket.WIDTH/2, self.rocket.HEIGHT/2]
        self.rocket.leg_body_r.position = self.rocket.position + [self.rocket.WIDTH/2, self.rocket.HEIGHT/2]
        # GYM ELEMENTS
        self.action_space, self.observation_space = self.__get_spaces()

    def __init__(self, render_mode = 'fast', seed = rand.random()):
        self.running = True
        self.screen = pygame.display.set_mode(self.WINDOW_RESOLUTION)
        self.clock = pygame.time.Clock()

        self.render_mode = render_mode
        self.__init_landing_scenario(seed)
        self.LANDER_INSTANCES.append(self)

    # GYM FUNCTIONS
    def reset(self, *, seed = None, options = None):
        super().reset(seed=seed)
        self.__init_landing_scenario(seed)
        return self.step(0)[0], {}

    def step(self, action):
        # TRANSLATE MODEL ACTION TO CONTROL INPUTS
        self.handle_inputs(action)

        # RUN SIMULATION STEP
        delta_time = self.clock.tick(self.FPS)/1000 if self.render_mode == "human" else 2/(3*self.FPS)
        self.handle_logic(delta_time)

        # CALCULATE OBSERVATIONS
        observations = self.__get_observations()

        # CALCULATE REWARD
        reward, terminated = self.__get_reward(delta_time)

        if self.render_mode in ["human", "fast"] and self.RENDER_TOGGLE:
            if self.render_mode == "human":
                self.camera.position = self.LANDER_INSTANCES[0].rocket.position
            self.render()

        return np.array(observations, dtype=np.float32), reward, terminated, False, {}

    # GAME FUNCTIONS
    def handle_inputs(self, action):
        if self == self.LANDER_INSTANCES[0]:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        self.running = False
                    case pygame.MOUSEWHEEL:
                        self.camera.scale *= 1.1 if event.y > 0 else 0.9
                    case pygame.KEYDOWN:
                        if action == None:
                            match event.key:
                                case pygame.K_a:
                                    self.in_left = True
                                case pygame.K_d:
                                    self.in_right = True
                                case pygame.K_w:
                                    self.in_up = True
                    case pygame.KEYUP:
                        if action == None:
                            match event.key:
                                case pygame.K_a:
                                    self.in_left = False
                                case pygame.K_d:
                                    self.in_right = False
                                case pygame.K_w:
                                    self.in_up = False
                        if event.key == pygame.K_SPACE:
                            self.RENDER_TOGGLE = not self.RENDER_TOGGLE
        if action != None:
            match action:
                case 0:
                    self.in_left = False
                    self.in_right = False
                    self.in_up = False
                case 1:
                    self.in_up = True
                    self.in_left = False
                    self.in_right = False
                case 2:
                    self.in_up = True
                    self.in_left = True
                    self.in_right = False
                case 3:
                    self.in_up = True
                    self.in_left = False
                    self.in_right = True

    def handle_logic(self, dt):
        self.rocket.thruster_power = float(self.in_up)
        self.rocket.thruster_vector = float(self.in_left) - float(self.in_right)
        self.rocket.thrust()
        self.rocket.update_collisions()
        self.planet.update_collisions()

        self.space.step(dt)

    def render(self):
        if self != self.LANDER_INSTANCES[0]:
            return
        self.screen.fill(self.BACKGROUND_COLOR)
        self.planet.draw(self.screen, self.camera)
        for instance in self.LANDER_INSTANCES:
            instance.rocket.draw(self.screen, self.camera)
        pygame.display.update()

    def run(self):
        pygame.init()
        while self.running:
            [_, reward, terminated, _, _] = self.step(None)
            #print(reward)
            if terminated: self.reset()
        pygame.quit()

if __name__ == "__main__":
    lander = RocketLander(render_mode = "human")
    lander.run()