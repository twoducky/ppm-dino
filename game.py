import pygame
from Entity import entities
from Component import components
from System import systems
import os

# Initialize pygame
pygame.init()
clk = pygame.time.Clock()
font = pygame.font.SysFont('Leelawadee', 18)

# Open a display
srf = pygame.display.set_mode((1202, 300))

# Flags and constants
fps = 30
dt = 0.4166
score = 0
pause = True
loop_flag = True
show_collisions = False
start = False

em = entities.EntityManager()


def save_image():
    pygame.image.save(srf, os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'assets/screencaps/', 'screencap_' + str(score) + '.png')))


def setup():
    # Create World
    world_id = em.create_new_entity()
    world = entities.World()
    em.add_component(components.Scroll(world.scroll), world_id)
    em.add_component(components.Render(world.render), world_id)
    em.add_component(components.Position(world.position), world_id)
    em.add_component(components.World(world_id, world.states), world_id)

    # Create Dino
    dino_id = em.create_new_entity()
    dino = entities.Dino()
    em.add_component(components.Position(dino.position), dino_id)
    em.add_component(components.Render(dino.render), dino_id)
    em.add_component(components.Collidee(), dino_id)
    em.add_component(components.Jump(dino.jump), dino_id)
    em.add_component(components.Collidee(), dino_id)
    em.add_component(components.Dino(dino_id), dino_id)
    return dino_id, world_id


Dino, World = setup()

sm = systems.SystemManager(em, srf, World, entities.Cactus(), Dino)
cm = components.ComponentManager()


def update():
    global score, pause
    if not pause and start:
        if sm.game_state is 'starting':
            score += 1
        sm.update()


def draw():
    sm.draw()


def restart_game():
    global score, pause
    pause = False
    score = 0
    sm.push_events('state_change', (World, 'Scroll'))
    sm.game_state = 'reset'


def start_game():
    sm.push_events('state_change', (Dino, 'Run'))
    sm.push_events('state_change', (World, 'Scroll'))


while loop_flag:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            loop_flag = False
        if e.type == pygame.QUIT:
            loop_flag = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_p:
                pause = not pause
            if e.key == pygame.K_c:
                show_collisions = not show_collisions
                if show_collisions:
                    sm.push_events('show_collision', True)
                else:
                    sm.push_events('show_collision', False)
            if e.key == pygame.K_s:
                if not start and score == 0:
                    start = True
                    pause = False
                    start_game()
                elif start and score > 1:
                    restart_game()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_q:
                save_image()
            if e.key == pygame.K_SPACE:
                dino_state = em.get_component_of_class(components.Render, Dino).state
                if dino_state is not 'Jump':
                    if dino_state is not 'Dead':
                        sm.push_events('state_change', (Dino, 'Jump'))

    # Clear the screen
    srf.fill((0, 0, 0))

    # Update
    update()

    # Draw
    draw()

    # Display Score
    text = str(score)
    color = (0, 255, 165)
    surface = font.render(text, True, color)
    srf.blit(surface, (500, 20))

    # Show Collisions
    if show_collisions:
        text = 'Show Collisions: ON'
        color = (238, 130, 238)
    else:
        text = 'Show Collisions: OFF'
        color = (200, 200, 200)
    surface = font.render(text, True, color)
    srf.blit(surface, (1000, 20))

    # Pause
    if pause:
        text = 'PAUSE'
        color = (0, 255, 165)
        surface = font.render(text, True, color)
        srf.blit(surface, (500, 60))

    # GAME OVER
    if sm.game_state is 'game_over':
        text = 'GAME OVER'
        color = (0, 255, 165)
        surface = font.render(text, True, color)
        srf.blit(surface, (500, 60))

    # Render
    pygame.display.flip()

    # Try to keep the specified frame rate
    clk.tick(fps)
