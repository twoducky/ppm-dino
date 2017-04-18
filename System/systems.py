from Component import components as mc
import random
import pygame

dt = 0.4


class SystemManager:
    def __init__(self, entity_manager, screen, world, cactus, dino):
        self.events = {}
        self.messages_and_callbacks = {}
        self.em = entity_manager
        self.game_state = 'starting'

        # Load Systems
        self.movement_system = MovementSystem(self.em, self)
        self.scroll_system = ScrollSystem(self.em, self)
        self.state_system = StateSystem(self.em, self)
        self.jump_system = JumpSystem(self.em, self, world)
        self.cactus_system = CactusSystem(self.em, self, world, cactus)
        self.render_system = RenderSystem(self.em, self, screen)
        self.collider_system = ColliderSystem(self.em, self)
        self.dino_system = DinoSystem(self.em, self)
        self.ai_system = AISystem(self.em, self, dino)
        self.gui_system = GUISystem(self.em, self, screen)

    def update(self):
        if self.game_state is not 'game_over':
            if self.game_state is not 'reset':
                self.movement_system.update()
                self.scroll_system.update()
                self.jump_system.update()
                self.cactus_system.update()
                self.collider_system.update()
                self.ai_system.update()
        if self.game_state is 'reset':
            self.cactus_system.reset()
            self.dino_system.reset()
            self.game_state = 'starting'
        self.clear_events()

    def draw(self):
        self.cactus_system.clear_off_screen()
        self.render_system.update()

    def push_events(self, message, targets):
        if message in self.events:
            self.events[message].append(targets)
        else:
            self.events[message] = [targets]

    def subscribe(self, messages_and_callbacks):
        for e, c in messages_and_callbacks.items():
            if e in self.messages_and_callbacks:
                self.messages_and_callbacks[e].append(c)
            else:
                self.messages_and_callbacks[e] = [c]

    def clear_events(self):
        current_events = self.events.copy()
        self.events = {}
        for event, targets in current_events.items():
            for target in targets:
                for callback in self.messages_and_callbacks[event]:
                    callback(target)


class AISystem:
    def __init__(self, entity_manager, system_manager, dino):
        self.em = entity_manager
        self.sm = system_manager
        self.dino = dino

    def update(self):
        state = self.em.get_component_of_class(mc.Render, self.dino).state
        cacti = self.em.get_all_entities_possessing_component(mc.Cactus)
        for cactus in cacti:
            position = self.em.get_component_of_class(mc.Position, cactus).position
            render = self.em.get_component_of_class(mc.Render, cactus)
            width = render.render[render.state][0][2]
            mid_point = position[0] + (width / 2)
            if mid_point < 200 and state is not 'Jump':
                self.sm.push_events('state_change', (self.dino, 'Jump'))


class StateSystem:
    def __init__(self, entity_manager, system_manager):
        self.em = entity_manager
        self.sm = system_manager
        self.sm.subscribe({'state_change': self.change_state})

    def change_state(self, eidNstate):
        eid, state = eidNstate
        renderee = self.em.get_component_of_class(mc.Render, eid)
        renderee.state = state


class DinoSystem:
    def __init__(self, entity_manager, system_manager):
        self.em = entity_manager
        self.sm = system_manager
        self.sm.subscribe({'collision': self.collide})

    def collide(self, colObs):
        collidee, collider = colObs
        dino = self.em.get_component_of_class(mc.Dino, collidee)
        if dino:
            self.sm.game_state = 'game_over'
            self.sm.push_events('state_change', (collidee, 'Dead'))

    def reset(self):
        dinos = self.em.get_all_entities_possessing_component(mc.Dino)
        for dino in dinos:
            self.em.get_component_of_class(mc.Position, dino).position = [5, 300]
            self.em.get_component_of_class(mc.Jump, dino).velocity = 0
            self.sm.push_events('state_change', (dino, 'Run'))


class JumpSystem:
    def __init__(self, entity_manager, system_manager, world):
        self.em = entity_manager
        self.sm = system_manager
        self.sm.subscribe({'state_change': self.jump})
        self.world = world

    def jump(self,  eidNstate):
        eid, state = eidNstate
        jumper = self.em.get_component_of_class(mc.Jump, eid)
        if jumper and state is 'Jump':
            position = self.em.get_component_of_class(mc.Position, eid).position
            world = self.em.get_component_of_class(mc.World, self.world)

            # Kinematics
            jumper.velocity = jumper.jump
            jumper.velocity += world.gravity * dt
            position[1] += jumper.velocity * dt

            # Set state
            self.em.get_component_of_class(mc.Render, eid).state = 'Jump'

    def update(self):
        world = self.em.get_component_of_class(mc.World, self.world)
        jumping_entities = self.em.get_all_entities_possessing_component(mc.Jump)
        for jumper in jumping_entities:
            jump = self.em.get_component_of_class(mc.Jump, jumper)
            position = self.em.get_component_of_class(mc.Position, jumper).position
            state = self.em.get_component_of_class(mc.Render, jumper).state
            if position[1] < world.ground and state is not 'Dead':
                jump.velocity += world.gravity * dt
                position[1] += jump.velocity * dt
                if position[1] > world.ground:
                    jump.velocity = 0
                    position[1] = world.ground
                    self.em.get_component_of_class(mc.Render, jumper).state = 'Run'


class CactusSystem:
    def __init__(self, entity_manager, system_manager, world, cactus):
        self.em = entity_manager
        self.sm = system_manager
        self.world = world
        self.cactus = cactus
        self.distance = 0

    def create_cactus(self):
        cactus_id = self.em.create_new_entity()
        chance = random.randint(0, 10)
        state = list(self.cactus.render['States'].keys())[chance]

        self.em.add_component(mc.Render(self.cactus.render), cactus_id)
        self.em.add_component(mc.Movement(self.cactus.movement), cactus_id)
        self.em.add_component(mc.Position(self.cactus.position), cactus_id)
        self.em.add_component(mc.Collider(), cactus_id)
        self.em.add_component(mc.Cactus(cactus_id, state), cactus_id)

        self.em.get_component_of_class(mc.Render, cactus_id).state = state

    def clear_off_screen(self):
        cacti = self.em.get_all_entities_possessing_component(mc.Cactus)
        for cactus_id in cacti:
            position = self.em.get_component_of_class(mc.Position, cactus_id).position
            renderee = self.em.get_component_of_class(mc.Render, cactus_id)
            if position[0] < -renderee.render[renderee.state][0][2]:
                self.em.remove_entity(cactus_id)

    def update(self):
        world_position = self.em.get_component_of_class(mc.Position, self.world).position
        if abs(world_position[0] - self.distance) > 400 and abs(world_position[0]) > 300:
            chance = random.randint(1, 50)
            if chance > 48:
                self.create_cactus()
                self.distance = world_position[0]

    def reset(self):
        cacti = self.em.get_all_entities_possessing_component(mc.Cactus)
        for cactus_id in cacti:
            self.em.remove_entity(cactus_id)


class GUISystem:
    def __init__(self, entity_manager, system_manager, screen):
        self.em = entity_manager
        self.sm = system_manager
        self.srf = screen
        self.sm.subscribe({'render_box': self.render_box})

    def render_box(self, box):
        box_min_x, box_min_y, box_max_x, box_max_y = box
        pygame.draw.rect(self.srf, (255, 255, 255),
                         (box_min_x, box_max_y, box_max_x - box_min_x, box_min_y - box_max_y), 2)


class ColliderSystem:
    def __init__(self, entity_manager, system_manager):
        self.em = entity_manager
        self.sm = system_manager
        self.show_collision = False
        self.sm.subscribe({'show_collision': self.trigger_collision})

    def update(self):
        collidee_entities = self.em.get_all_entities_possessing_component(mc.Collidee)
        collider_entities = self.em.get_all_entities_possessing_component(mc.Collider)
        for collidee in collidee_entities:
            collidee_render = self.em.get_component_of_class(mc.Render, collidee)
            collidee_position = self.em.get_component_of_class(mc.Position, collidee).position
            renderee_width = collidee_render.render[collidee_render.state][0][2]
            renderee_height = collidee_render.render[collidee_render.state][0][3]
            box1_min_x = collidee_position[0] + 15
            box1_min_y = collidee_position[1] - 15
            box1_max_x = collidee_position[0] + renderee_width - 15
            box1_max_y = collidee_position[1] - renderee_height
            if self.show_collision:
                self.sm.push_events('render_box', (box1_min_x, box1_min_y, box1_max_x, box1_max_y))
            for collider in collider_entities:
                collider_render = self.em.get_component_of_class(mc.Render, collider)
                collider_position = self.em.get_component_of_class(mc.Position, collider).position
                renderer_width = collider_render.render[collider_render.state][0][2]
                renderer_height = collider_render.render[collider_render.state][0][3]
                if self.check_collision((box1_min_x, box1_min_y, box1_max_x, box1_max_y),
                                        (collider_position, renderer_width, renderer_height)):
                    self.sm.push_events('collision', (collidee, collider))

    def check_collision(self, box1, box2):
        box1_min_x, box1_min_y, box1_max_x, box1_max_y = box1
        box2_pos, box2_width, box2_height = box2
        box2_min_x = box2_pos[0]
        box2_min_y = box2_pos[1]
        box2_max_x = box2_pos[0] + box2_width
        box2_max_y = box2_pos[1] - box2_height

        if self.show_collision:
            self.sm.push_events('render_box', (box2_min_x, box2_min_y, box2_max_x, box2_max_y))

        d1x = box1_min_x - box2_max_x
        d1y = box1_min_y - box2_max_y
        d2x = box2_min_x - box1_max_x
        d2y = box2_min_y - box1_max_y

        if d1x < 0 and d1y > 0 and d2x < 0 and d2y > 0:
            return True
        return False

    def trigger_collision(self, state):
        self.show_collision = state


class MovementSystem:
    def __init__(self, entity_manager, system_manager):
        self.em = entity_manager
        self.sm = system_manager

    def update(self):
        moving_entities = self.em.get_all_entities_possessing_component(mc.Movement)
        for mover in moving_entities:
            velocity = self.em.get_component_of_class(mc.Movement, mover).velocity
            position = self.em.get_component_of_class(mc.Position, mover).position
            position[0] += velocity * dt


class ScrollSystem:
    def __init__(self, entity_manager, system_manager):
        self.em = entity_manager
        self.sm = system_manager

    def update(self):
        scrolling_entities = self.em.get_all_entities_possessing_component(mc.Scroll)
        for scroller in scrolling_entities:
            scroll = self.em.get_component_of_class(mc.Scroll, scroller).scroll
            position = self.em.get_component_of_class(mc.Position, scroller).position
            vel = scroll
            position[0] += vel * dt


class RenderSystem:
    def __init__(self, entity_manager, system_manager, screen):
        self.em = entity_manager
        self.sm = system_manager
        self.srf = screen

    def update(self):
        rendering_entities = self.em.get_all_entities_possessing_component(mc.Render)
        for renderer in rendering_entities:
            rend = self.em.get_component_of_class(mc.Render, renderer)
            position = self.em.get_component_of_class(mc.Position, renderer).position

            # Render animation
            rend.animations[rend.state].blit(self.srf, (position[0], position[1] - rend.render[rend.state][0][3]))

            # For scrolling objects
            if self.em.get_component_of_class(mc.Scroll, renderer):
                if position[0] < -rend.render[rend.state][0][2] + 1202:
                    rend.animations[rend.state].blit(self.srf, (
                        position[0] + rend.render[rend.state][0][2], position[1] - rend.render[rend.state][0][3]))
                if position[0] < -rend.render[rend.state][0][2]:
                    position[0] = 0
