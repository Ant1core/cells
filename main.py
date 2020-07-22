import pygame
import time
import random
import math
import numpy
from pygame import gfxdraw
import pandas as pd

game_width = 800
game_height = 600
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
fps = 60

# bot params
bots=[]
health = 100
size = 5
max_speed = 1
max_age = 500
df_bots = pd.DataFrame()

# area params
df_food = pd.DataFrame()
food = []
area_food_dens = 1
nutrition = 10

def magnitude_calc(vector):
    x = 0
    for i in vector:
        x += i**2
    magnitude = x**0.5
    return(magnitude)

def normalise(vector):
    magnitude = magnitude_calc(vector)
    if magnitude != 0:
        vector = vector/magnitude
    return(vector)

def lerp():
    percent_health = bot.health/health
    lerped_colour = (max(min((1-percent_health)*255,255),0), max(min(percent_health*255,255),0), 0)
    return(lerped_colour)


gameDisplay =pygame.display.set_mode((game_width, game_height))
clock = pygame.time.Clock()

####################    BOT CLASS

class create_bot():
    def __init__(self, x, y, type):
        self.position = numpy.array([x,y], dtype='float64')
        if type == 1:
            self.color = green
        if type == 2:
            self.color = red
        self.health = health
        self.size = 5
        self.age = 1
        self.type = type
        self.acceleration = numpy.array([1,2], dtype='float64')

    def draw_bot(self):
        pygame.gfxdraw.aacircle(gameDisplay, int(self.position[0]), int(self.position[1]), self.size, black)
        pygame.gfxdraw.filled_circle(gameDisplay, int(self.position[0]), int(self.position[1]), self.size, self.color)

    def move_vector(self, target):
        desired_acc = numpy.add(target, -self.position)
        desired_acc = normalise(desired_acc)
        velocity_vector = normalise(self.acceleration) + desired_acc
        if self.type == 1:
            self.acceleration = velocity_vector * max_speed
        if self.type == 2:
            self.acceleration = velocity_vector * max_speed*1.2

    def seek_food(self, list_of_stuff):
        closest = []
        closest_distance = max(game_width,game_height)
        bot_x = self.position[0]
        bot_y = self.position[1]
        item_number = len(list_of_stuff)
        index = 0
        if self.type == 1:
            for x in range(item_number):
                i = list_of_stuff[x]
                item_x = i[0]
                item_y = i[1]
                distance = math.hypot(bot_x-item_x, bot_y-item_y)

                if distance < self.size:
                    list_of_stuff.pop(x)
                    self.health += nutrition
                    self.size += 1

                if distance < closest_distance:
                    closest_distance = distance
                    closest = [item_x, item_y]

        if self.type == 2:
            for x in range(item_number):
                i = list_of_stuff[x]
                if i.type == 1:
                    item_x = i.position[0]
                    item_y = i.position[1]
                    distance = math.hypot(bot_x-item_x, bot_y-item_y)

                    if (distance < self.size/2) and (distance != 0):
                        list_of_stuff.pop(x)
                        self.health += nutrition
                        self.size += 1

                    if (distance < closest_distance) and (distance != 0):
                        closest_distance = distance
                        closest = [item_x, item_y]
        return closest

    def collide(self, bots):
        closest = []
        closest_distance = max(game_width,game_height)
        bot_x = self.position[0]
        bot_y = self.position[1]
        item_number = len(bots)

        for i in bots:
            if i.type == self.type:
                item_x = i.position[0]
                item_y = i.position[1]
                item_vector = [0-item_x, 0-item_y]
                distance = math.hypot(bot_x-item_x, bot_y-item_y)
                dist_size = i.size + self.size
                if distance < dist_size:
                    item_vel = numpy.add(item_vector, self.position)
                    item_vel = normalise(item_vel)
                    self.acceleration = item_vel * max_speed/2


    def dead(self):
        if (self.health > 0) and (self.age < max_age):
            return(False)
        else:
            if self.position[0] < game_width and self.position[1] < game_height:
                food.append(self.position)
            return(True)

    def reproduce(self):
        if self.health > 100:
            bots.append(create_bot(self.position[0]+self.size*1.5, self.position[1]+self.size*1.5, self.type))
            self.health /= 2
            self.size = int(round(self.size / 2))

    def update(self):
        if self.dead():
            bots.remove(bot)
        self.reproduce()
        self.position += self.acceleration
        self.health -= 0.1
        self.age += 1
        #self.color = lerp()


for i in range(20):
    bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height), 1))

for i in range(5):
    bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height), 2))

#################################
running = True
while(running):
    gameDisplay.fill(white)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if random.random() < area_food_dens:
        food.append(numpy.array([random.uniform(0, game_width), random.uniform(0, 300)], dtype='float64'))
    if random.random() < area_food_dens:
        food.append(numpy.array([random.uniform(0, game_width), random.uniform(0, game_height)], dtype='float64'))
    for bot in bots:
        #target = numpy.array([200,200], dtype='float64')
        try:

            if bot.type == 1:
                bot.collide(bots)
                target = bot.seek_food(food)
            if bot.type == 2:
                bot.collide(bots)
                target = bot.seek_food(bots)
            bot.move_vector(target)
            bot.update()
            bot.draw_bot()
        except:
            bot.collide(bots)
            bot.update()
            bot.draw_bot()


    for i in food:
        pygame.draw.circle(gameDisplay, (150,150,0), (int(i[0]), int(i[1])), 2)

    pygame.display.update()
    clock.tick(fps)
pygame.quit()
