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
    def __init__(self,width,height,seed=False):
        if seed:
            self.seed = seed
        else:
            self.seed = str(random.randint(1,999999999999)) # if no seed was given, use a random number
        
        self.width = width
        self.height = height
        self.setup()

    def setup(self):
        self.rng = random.Random()          #create random number generator for this instance
        self.rng.seed(self.seed) # and initialise it with the seed
        self.surface = pygame.Surface([self.width,self.height])

        self.gain = self.rng.randint(MinGain,MaxGain)
        self.colour_mode = self.rng.randint(0,5)
        self.hue_offset = self.rng.randint(0,359)

    def makePicture(self):
        self.setup()
        self.find()
        self.calculate()
        self.draw()
        pygame.image.save(self.surface,"{}.png".format(self.seed))

    def find(self,target=False):
        self.highest = 0
        self.lowest = 550
        attempts = 0
        while self.highest - self.lowest < HuntTarget:
            self.highest = 0
            self.lowest = 550
            if not target:
                self.zoom_offset_x = self.rng.uniform(-2,2)
                self.zoom_offset_y = self.rng.uniform(-2,2)
                self.zoom_pixel = self.rng.uniform(MinZoom,MaxZoom)
            else:
                self.zoom_offset_x = self.rng.uniform(target[0],target[1])
                self.zoom_offset_y = self.rng.uniform(target[2],target[3])
                
            for points in range(200): #Pick 100 random points and check how varied they are
                x = self.rng.randint(0,self.width)
                y = self.rng.randint(0,self.height)
                self.getPixel(x,y)
            attempts += 1
        print("found one with {0} range. {1} attempts".format(self.highest - self.lowest,attempts))

    def findZoom(self,zoom):
        backup = (self.zoom_offset_x,self.zoom_offset_y,self.zoom_pixel)
        rangex = (self.zoom_offset_x,(self.width*self.zoom_pixel)+ self.zoom_offset_x)
        rangey = (self.zoom_offset_y,(self.height*self.zoom_pixel)+ self.zoom_offset_y)
        
        self.zoom_pixel = zoom
        
        self.highest = 0
        self.lowest = 550
        while self.highest - self.lowest < HuntTarget:
            self.highest = 0
            self.lowest = 550
            self.zoom_offset_x = self.rng.uniform(rangex[0],rangex[1])
            self.zoom_offset_y = self.rng.uniform(rangey[0],rangey[1])
            for points in range(100): #Pick 100 random points and check how varied they are
                x = self.rng.randint(0,self.width)
                y = self.rng.randint(0,self.height)
                self.getPixel(x,y)

        centrex = self.zoom_offset_x+(zoom*self.width/2)
        centrey = self.zoom_offset_y+(zoom*self.height/2)
        retval = (self.zoom_offset_x,self.zoom_offset_y,self.zoom_pixel,centrex,centrey)
        self.calculate()
        self.draw()
        pygame.image.save(self.surface,"{}-end.png".format(self.seed))
        
        self.zoom_offset_x = backup[0]
        self.zoom_offset_y = backup[1]
        self.zoom_pixel = backup[2]
        return retval

    def animateZoom(self,frames,zoom_per_frame):
        self.setup()
        self.find()
        
        endzoom = self.zoom_pixel
        for i in range(frames):
            widthpix = endzoom * (self.width-zoom_per_frame)
            endzoom = widthpix / self.width
            
        zoom_end = self.findZoom(endzoom)
        
        xdelta = ( zoom_end[0] - self.zoom_offset_x )/frames
        ydelta = ( zoom_end[1] - self.zoom_offset_y )/frames
        for i in range(frames):
            print("frame {0} of {1}".format(i,frames))
            widthpix = self.zoom_pixel * (self.width-zoom_per_frame)
            self.zoom_pixel = widthpix / self.width
            
            self.zoom_offset_x = zoom_end[3]-(self.zoom_pixel*self.width/2)
            self.zoom_offset_y = zoom_end[4]-(self.zoom_pixel*self.height/2)            
            
            self.calculate()
            self.draw()
            pygame.image.save(self.surface,"{0}_{1:04}.png".format(self.seed,i))
        import subprocess
        subprocess.Popen(["ffmpeg","-i","{0}_%04d.png".format(self.seed),"{}.mp4".format(self.seed)]).wait()
            
            
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
    x = 500
    y = 320
    mandel = Mandelbrot(x,y,sys.argv[1])
    #screen = pygame.display.set_mode((x,y))
    #mandel.makePicture()
    #screen.blit(mandel.surface,(0,0))
    #pygame.display.flip()
    #print("X {0} to {1}".format( mandel.zoom_offset_x,(x*mandel.zoom_pixel)+ mandel.zoom_offset_x))
    #print("Y {0} to {1}".format( mandel.zoom_offset_y,(y*mandel.zoom_pixel)+ mandel.zoom_offset_y))
    #import time
    #time.sleep(5)
    mandel.animateZoom(200,8)
    
