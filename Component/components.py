import pygame
import os
import pyganim as pyg


class ComponentManager:
    def __init__(self):
        pass


class Position:
    def __init__(self, position):
        self.position = [0, 0]
        self.position[0] = position[0]
        self.position[1] = position[1]


class Jump:
    def __init__(self, jump):
        self.jump = jump
        self.velocity = 0


class Collider:
    def __init__(self):
        pass


class Collidee:
    def __init__(self):
        pass


class Render:
    def __init__(self, render):
        self.path = render['Path']
        self.states = render['States']
        self.render = render
        self.animations = {}
        self.state = 'Idle'
        self.setup()

    def setup(self):
        buff = {}
        spritesheet = pygame.image.load(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', self.path)))

        for k, v in self.states.items():
            buff[k] = []
            for i in range(v):
                buff[k].append((spritesheet.subsurface(self.render[k][i]), 200))
            self.animations[k] = pyg.PygAnimation(buff[k])
            self.animations[k].play()


class Movement:
    def __init__(self, velocity):
        self.velocity = velocity


class Scroll:
    def __init__(self, scroll):
        self.scroll = scroll


class World:
    def __init__(self, eid, state):
        self.eid = eid
        self.gravity = state['Gravity']
        self.ground = state['Ground']


class Dino:
    def __init__(self, eid):
        self.eid = eid


class Cactus:
    def __init__(self, eid, state):
        self.eid = eid
        self.state = state
