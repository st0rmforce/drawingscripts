import math, cmath, random
import pygame
from pygame.locals import *

MinGain=100
MaxGain=300
MinZoom=pow(10,-13) #tiiiiiiny
MaxZoom=0.0001
HuntTarget = 100

def mandelPixel(x,y,gain,off_x=0,off_y=0):
    if x > 2 or y > 2:
        return 0,0
    c = complex(x,y)
    cursor = complex(off_x,off_y)
    count = 0
    while cmath.polar(cursor)[0] < 2 and count < gain:
        cursor = (cursor*cursor)+c
        count += 1
    return count,cmath.polar(cursor)[0]


class Mandelbrot:
    def __init__(self,width,height,seed=False,rng=random.Random()):
        if seed:
            self.rng = random.Random()
            self.rng.seed(seed)
        else:
            self.rng = rng
        
        self.width = width
        self.height = height
        self.surface = pygame.Surface([width,height])

        self.gain = self.rng.randint(MinGain,MaxGain)
        self.colour_mode = self.rng.randint(0,5)
        self.hue_offset = self.rng.randint(0,359)
        
        self.find()
        self.calculate()
        self.draw()

    def find(self):
        self.highest = 0
        self.lowest = 550
        while self.highest - self.lowest < HuntTarget:
            self.highest = 0
            self.lowest = 550
            self.zoom_offset_x = self.rng.uniform(-2,2)
            self.zoom_offset_y = self.rng.uniform(-2,2)
            self.zoom_pixel = self.rng.uniform(MinZoom,MaxZoom)
            for points in range(200): #Pick 100 random points and check how varied they are
                x = self.rng.randint(0,self.width)
                y = self.rng.randint(0,self.height)
                self.getPixel(x,y)
        print("found one with {} range".format(self.highest - self.lowest))

    def getPixel(self,x,y):
        pix_x = (x*self.zoom_pixel)+ self.zoom_offset_x
        pix_y = (y*self.zoom_pixel)+ self.zoom_offset_y
        step, magnitude = mandelPixel(pix_x,pix_y,self.gain)
        self.highest = max(self.highest,step)
        self.lowest = min(self.lowest,step)
        return step,magnitude

    def calculate(self):
        self.pixels = []
        
        for x in range(self.width):
            self.pixels.append([])
            print(" {0}%".format(int((x/self.width)*100)),end="\r")
            for y in range(self.height):
                self.pixels[-1].append(self.getPixel(x,y))
        print("\n")

    def draw(self):
        for x in range(self.width):
            for y in range(self.height):
                self.drawPixel(x,y)


                
    def drawPixel(self,x,y):
        colour = pygame.Color("red")
        step = self.pixels[x][y][0]
        distance = self.pixels[x][y][1]
        if self.colour_mode > 5:
            self.colour_mode = 0
        if self.colour_mode == 0:
            step -= self.lowest
            hue = (int(step * (340.0/self.highest))+self.hue_offset)%360
            bright = int(step * (95.0/self.highest))
        elif self.colour_mode == 1:
            hue = int(step * (340.0/self.gain)+(distance*100)+self.hue_offset)%360
            bright = int(step * (99.0/self.gain))
        elif self.colour_mode == 2:
            hue = (int(step * (340.0/self.gain))+self.hue_offset)%360
            bright = int(step * (99.0/self.gain))
        elif self.colour_mode == 3:
            step -= self.lowest
            hue = int(step * (340.0/self.highest)+(distance*70)+self.hue_offset)%360
            bright = int(step * (95.0/self.highest))            
        elif self.colour_mode == 4:
            step -= self.lowest
            hue = int(step * (340.0/self.highest)+(distance*70)+self.hue_offset)%360
            target = ((self.highest-self.lowest)/2)+self.lowest
            if abs(step-target) < 5:
                bright = 100
            elif abs(step-target) < 7:
                bright = 85
            elif abs(step-target) < 10:
                bright = 60
            elif abs(step-target) < 15:
                bright = 40
            else:
                bright = 0           
        elif self.colour_mode == 5:
            step -= self.lowest
            hue = (int(step * (340.0/self.highest))+self.hue_offset)%360
            target = ((self.highest-self.lowest)/1.1)+self.lowest
            if abs(step-target) < 5:
                bright = 100
            elif abs(step-target) < 7:
                bright = 85
            elif abs(step-target) < 10:
                bright = 60
            elif abs(step-target) < 20:
                bright = 40
            else:
                bright = 0
                
        colour.hsva = (hue,100,bright,100)
        self.surface.set_at((x,y), colour)



import sys
if __name__ == "__main__":
    print(sys.argv[1])
    x = 1920
    y = 1080
    mandel = Mandelbrot(x,y,sys.argv[1])
    screen = pygame.display.set_mode((x,y))
    screen.blit(mandel.surface,(0,0))
    pygame.display.flip()
    pygame.image.save(mandel.surface,"{}.png".format(sys.argv[1]))
    print("X {0} to {1}".format( mandel.zoom_offset_x,(x*mandel.zoom_pixel)+ mandel.zoom_offset_x))
    print("Y {0} to {1}".format( mandel.zoom_offset_y,(y*mandel.zoom_pixel)+ mandel.zoom_offset_y))
    import time
    time.sleep(5)
