import pygame
import random
import time
from pathlib import Path
from myhyper import *

def partition_maker(func, mod):
    sets = [set([i,func(i) % mod]) for i in range(mod)]
    completion = True
    while completion:
        completion = False
        for s in sets:
            for d in sets:
                if not s == d and not s & d == set([]) and not completion:
                    s.update(d)
                    sets.remove(d)
                    completion = True
    return sets

def get_part_of(partition, value):
    for part in partition:
        if value in part:
            return part
    return -1

def graph_maker(func, mod):
    if type(func) is dict:
        graph = []
        for val in range(mod):
            graph.extend([(val, val2) for val2 in func[val]])
    else:
        graph = [(val, func(val) % mod) for val in range(mod)]
    return graph

random.seed()

def intersecting_segs(x1, y1, x2, y2, x3, y3, x4, y4):
    ox1 = max(min(x1,x2), min(x3,x4))
    ox2 = min(max(x1,x2), max(x3,x4))
    oy1 = max(min(y1,y2), min(y3,y4))
    oy2 = min(max(y1,y2), max(y3,y4))
    if ox2 < ox1 or oy2 < oy1:
        return False
    try:
        mA = (y2 - y1) / (x2 - x1)
        mB = (y4 - y3) / (x4 - x3)
        x = (y3 - y1 + mA*x1 - mB*x3) / (mA - mB)
    except ZeroDivisionError:
        return False
    if not ox1 < x < ox2:
        return False
    y = y1 + mA * (x - x1)
    if not oy1 < y < oy2:
        return False
    return True

class Node:
    def __init__(self, value):
        self.value = value
        self.x = random.randint(buffer, boardWidth-buffer)
        self.y = random.randint(buffer, boardHeight-buffer)
        self.velx = 0
        self.vely = 0
    def dist_and_dir_to(self, node2):
        change_x = node2.x - self.x
        change_y = node2.y - self.y
        dist = ( (change_x)**2 + (change_y)**2 )**0.5
        if (dist**2)**0.5 <= 0.001:
            dist = 0.001
        unit_x = change_x / dist
        unit_y = change_y / dist
        return dist, unit_x, unit_y
    def apply_spring_force(self, node2, dt):
        dist, unit_x, unit_y = self.dist_and_dir_to(node2)
        force = spring_const * (dist - spring_length)
        force_x = force*unit_x
        force_y = force*unit_y
        self.update_vel(force_x * dt, force_y * dt)
        node2.update_vel(-force_x * dt, -force_y * dt)
    def apply_electron_force(self, partition, node2, dt):
        dist, unit_x, unit_y = self.dist_and_dir_to(node2)
        #for beauty, use both; for equal distances, use first
        home_molecule = get_part_of(partition, self.value)
        if dist < max_elec_force_dist or node2.value in home_molecule:
            force = -1 * electron_const / (dist**2)**(0.5*electron_force_power)
            force_x = force*unit_x
            force_y = force*unit_y
            self.update_vel(force_x * dt, force_y * dt)
            #if not there, causes movement and spinning!!
            node2.update_vel(-force_x * dt, -force_y * dt)
    def apply_drag_force(self, dt):
        force_x = -1 * drag_const * self.velx
        force_y = -1 * drag_const * self.vely
        self.update_vel(force_x * dt, force_y * dt)
    def apply_intersecting_force(self, list_graph, node_list, node2, dt):
        friendA = node_list[list_graph[self.value]]
        friendB = node_list[list_graph[node2.value]]
        if intersecting_segs(self.x, self.y, friendA.x, friendA.y,
                             node2.x, node2.y, friendB.x, friendB.y):
            dist, unit_x, unit_y = self.dist_and_dir_to(friendA)
            force_x = intersecting_const*unit_x
            force_y = intersecting_const*unit_y
            self.update_vel(force_x * dt, force_y * dt)
    def apply_edge_force(self, dt):
        out = False
        force_x, force_y = 0,0
        if not buffer <= self.x:
            force_x = edge_force
            out = True
        if not self.x <= boardWidth-buffer:
            force_x = -edge_force
            out = True
        if not buffer <= self.y:
            out = True
            force_y = edge_force
        if not self.y <= boardHeight-buffer:
            out = True
            force_y = -edge_force
        if out:
            self.update_vel(force_x * dt, force_y * dt)
    def update_vel(self, mx, my):
        self.velx += (mx / mass)
        self.vely += (my / mass)
    def update(self, dt):
        self.x += self.velx*dt
        self.y += self.vely*dt
    def get_draw_coords(self):
        return self.x * winWidth/boardWidth, self.y * winHeight/boardHeight
    def draw(self, screen):
        x, y = self.get_draw_coords()
        if do_numbers:
            pygame.draw.circle(screen, ball_color, (int(x), int(y)), win_radius)
            font = pygame.font.Font(None, int(16*(1000/boardWidth))) #16
            text = font.render(str(self.value), True, (255, 255, 255))
            screen.blit(text, (x-text.get_width()//2, y-text.get_height()//2))
        else:
            #alternate draw style
            #pygame.draw.circle(screen, (180,220,240), (int(x), int(y)), win_radius)
            #pygame.draw.circle(screen, ball_color,  (int(x), int(y)), win_radius//2)
            pygame.draw.circle(screen, ball_color, (int(x), int(y)), win_radius)
            pygame.draw.circle(screen, (180,200,220), (int(x), int(y)), int(win_radius*3/5))

def apply_forces(node_list, graph, list_graph, partition,
                 do_intersecting_force, do_drag_force, dt):
    #this function applies forces in a weird way, giving more or less than required
    #because of how it is set up.  However, it works, so I will not change it
    for node1 in node_list:
        for node2 in node_list:
            if node1 == node2:
                pass
            elif (node1.value, node2.value) in graph:
                node1.apply_spring_force(node2, dt)
            else:
                node1.apply_electron_force(partition, node2, dt)
                if do_intersecting_force:
                    node1.apply_intersecting_force(list_graph, node_list, node2, dt)
                pass
    for node in node_list:
        if do_drag_force:
            node.apply_drag_force(dt)
        if do_edge:
            node.apply_edge_force(dt)

def updates(node_list, dt):
    for node in node_list:
        node.update(dt)

def draw_background(mod, screen, name, do_intersecting_force):
    if do_intersecting_force:
        pygame.draw.circle(screen, (150, 0, 50), (winWidth - 100, winBuffer//2), 15)
    ratx = winWidth/boardWidth
    raty = winHeight/boardHeight
    pygame.draw.rect(screen, (0, 40, 0), (winBuffer, winBuffer,
                                          winWidth-2*winBuffer,
                                          winHeight-2*winBuffer), 5)
    font = pygame.font.Font(None, 40)
    text = font.render(name, True, ball_color)
    screen.blit(text, (winWidth*(1/2)-text.get_width()//2, winBuffer//2-text.get_height()//2))
    

def draw(mod, node_list, graph, screen, name, do_intersecting_force):
    screen.fill(back_color)
    if do_edge:
        draw_background(mod, screen, name, do_intersecting_force)
    if do_lines:
        for i, j in graph:
            if i == j:
                node = node_list[i]
                x, y = node.get_draw_coords()
                pygame.draw.circle(screen, ball_color, (int(x), int(y)), int(win_radius*3/2), 1)
            node1 = node_list[i]
            x1, y1 = node1.get_draw_coords()
            node2 = node_list[j]
            x2, y2 = node2.get_draw_coords()
            pygame.draw.line(screen, ball_color, (x1, y1), (x2, y2), win_line)
    for node in node_list:
        node.draw(screen)
    pygame.display.update()

def get_avg_spd(node_list):
    total_spd = 0
    for node in node_list:
        total_spd += (node.velx**2 + node.vely**2)**0.5
    return total_spd/len(node_list)

#node and board stuff
spring_const = 0.6 #0.6
electron_const = 300 #30
intersecting_const = 25
electron_force_power = 1 #1
max_elec_force_dist = 30 #100
drag_const =0.135 #0.135   0.08
edge_force = 10 #20
spring_length = 50 #30
dt = 0.3 #0.35,  0.5
mass = 1
radius = 9 #8
ball_color = (0, 100, 200) #(0, 100, 200)
back_color = (0,0,0)  #(255, 255, 255)
boardWidth = boardHeight = 900 #900
line = 2 #4
#pygame, window and display stuff
winWidth = 780 #1000
winHeight = 780 #750
winBuffer = 40 #50
buffer = int(winBuffer * boardWidth/winWidth)
win_radius = 1+int(radius * winWidth/boardWidth)
win_line = 1+int(line * winWidth/boardWidth)

#style stuff
do_lines = True
do_edge = True
do_numbers = True

#graph and modulus stuff
mod = 9
function_var = 9
function = lambda x : x ** function_var
function_name = "x ** " + str(function_var)
graph = graph_maker(function, mod)
partition = partition_maker(function, mod)

#creation of actual variables for the simulation

def run_mult(k, mod, show=True, save=False, wait=False):
   filename = -1
   if save:
       filename = "mult/"+str(k) + "m" + str(mod) + ".jpg"
   run_graph(lambda x : (x*k) % mod, mod,
             name=str(k)+"th multiplication mod "+str(mod), wait=wait, show=show, filename=filename)


def run_tetra(power, mod, show=True, save=False, wait=False):
   filename = -1
   if save:
       filename = "tetration/"+str(power) + "m" + str(mod) + ".jpg"
   run_graph(lambda x : tetration(x, power, mod), mod,
             name=str(power)+"th tetration mod "+str(mod), wait=wait, show=show, filename=filename)

def run_infinf(power, mod, show=True, save=False, wait=False):
    filename = -1
    if save:
        filename = "hyper_infinf/"+ "m" + str(mod) + ".jpg"
    run_graph(lambda x : tetration(x, float('inf'), mod), mod,
             name="infiniteth hyper-infinity of mod "+str(mod), wait=wait, show=show, filename=filename)

def run_prom(show=True, save=False, wait=True):
    filename = -1
    if save:
       filename = "prom/"+ str(random.randint(1, 10000)) + ".jpg"
    #    0  1  2  3  4  5  6  7  8  9  10  11  12  13  14
    p = [1, 2, 3, 4, 5, 6, 7, 2, 3, 3]
    r = [1, 2, 3, 4, 5, 6, 2, 8, 6, 3, 3]
    o = [1, 2, 3, 4, 5, 6, 0]
    m = [1, 2, 3, 4, 5, 3, 3, 3, 5, 5, 11, 12, 5]
    def func (x):
        chem = 0
        if chem <= x < chem + len(p):
            return chem + p[x]
        chem += len(p)
        if chem <= x < chem+len(r):
            return chem + r[x-chem]
        chem += len(r)
        if chem <= x < chem+len(o):
            return chem + o[x-chem]
        chem += len(o)
        if chem <= x < chem+len(m):
            return chem + m[x-chem]
    run_graph(func, len(p)+len(r)+len(o)+len(m),
             name="???", wait=wait, show=show, filename=filename)

def run_power(power, mod, show=True, save=False, wait=False):
    filename = -1
    if save:
        filename = "power/"+str(power) + "m" + str(mod) + ".jpg"
    run_graph(lambda x : x ** power, mod,
              name=str(power)+"th power mod "+str(mod), wait=wait, show=show, filename=filename)

def run_rand(mod, show=True, save=False, wait=False):
    cons = [random.randint(0, mod-1) for i in range (mod)]
    def func (x):
        return cons[x]
    filename = -1
    if save:
        filename = "random/"
        for i in cons:
            filename += str(i)
        filename += ".jpg"
    run_graph(func, mod, name="random connections", wait=wait, show=show, filename=filename)

def run_graph(function, mod, name="graph", show=True, filename=-1,
              wait=False, partit=None, keep_wiggle=False):
    if not filename == -1:
        if do_numbers:
            filename = "nums/" + filename
        filename = "graph_pics/" + filename
        my_file = Path(filename)
        print(filename)
        if my_file.is_file():
            # image for graph already saved
            return
    pygame.init()
    screen = pygame.display.set_mode((winWidth, winHeight))
    graph = graph_maker(function, mod)
    list_graph = [pair[1] for pair in graph]
    if partit:
        partition = partit
    else:
        partition = partition_maker(function, mod)
    do_intersecting_force = False
    do_drag_force = True

    node_list = list()
    node_list = [Node(val) for val in range(mod)]

    avg_spd = 0
    clock = pygame.time.Clock()
    stop = False
    while not stop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop = True
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        node_list = [Node(val) for val in range(mod)]
                    if event.key == pygame.K_i:
                        do_intersecting_force = not do_intersecting_force
        apply_forces(node_list, graph, list_graph, partition,
                     do_intersecting_force, do_drag_force, dt)
        updates(node_list, dt)
        if show:
            draw(mod, node_list, graph, screen, name, do_intersecting_force)
            #even out the frame rate, 60 fps
            #clock.tick(60)
        
        avg_spd = get_avg_spd(node_list)
        if avg_spd < 4 and keep_wiggle:
            do_drag_force = False
        if  avg_spd < 0.1:
            stop = True

    do_intersecting_force = False
    draw(mod, node_list, graph, screen, name, do_intersecting_force)

    user_okay = True
    if wait:
        stop = False
        while not stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop = True
                    user_okay = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        stop = True
                    if event.key == pygame.K_x:
                        user_okay = False
                        stop = True

    if not filename == -1 and user_okay:
        pygame.image.save(screen, filename)

    pygame.quit()

def generate_pics(run_func, p1, p2, m1, m2):
    for power in range(p1, p2):
        for mod in range(m1, m2):
            run_func(power, mod, show=False, save=True, wait=True)

#generate_pics(run_mult, 2, 8, 1, 16)
#run_power(2, 95)
#run_infinf(2, 89)
