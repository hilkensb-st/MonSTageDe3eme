import time,math,struct,gc
from ST7735 import *
from machine import Pin, SPI,I2C
from pyb import LED,delay,Accel,ADC,Pin,Timer,Switch,LED,RTC
#from font import terminalfont
from random import randint
from LPS22 import LPS22
from rotary_tim import Encoder

terminalfont={
    "Width":6,"Height":8,
    "Start":32,"End":127,
    "Data":bytearray(open('fnt.bin').read())}


sw = Switch()
acc = Accel()
i2c = I2C(2)
lps22 = LPS22(i2c)
spi = SPI(2, baudrate=60000000, polarity=0, phase=0)
t = TFT(spi, aDC="Y3", aReset="Y4",aCS='Y5')
t.initb2()
t.fill(0)

#########################################################################################################

def level_sensors_app():
    while True and not click:
        x,y,z = acc.filtered_xyz()
        print("x:%i y:%i z:%i" %(x,y,z))
        t.fillrect((0,80),(128,25),TFT.BLACK)
        t.fillrect((55,38),(35,100),TFT.BLACK)
        t.fillrect((64,80),(z//2,3),TFT.PURPLE)
        t.fillrect((64,80),(3,y//2),TFT.PURPLE)
        t.text((64+z//2,85),'%s' % z,0xFFFF,terminalfont,1)
        t.text((70,80+y//2),'%s' % y,0xFFFF,terminalfont,1)
        time.sleep(0.07)
        if sw(): return True

#########################################################################################################

class Ball:
    def __init__(self,max_x=128,max_y=128,color=None):
        self.max_x = max_x
        self.max_y = max_y
        self.x = randint(10,max_x-10)
        self.y = randint(10,max_y-10)
        self.xs = randint(-5,5)
        self.ys = randint(-5,5)

        if color is None:
            self.color = randint(100,128) << 11 |  randint(80,255) << 5 | randint(100,128)

    def __eq__(self, other):
        if  int(self.x-1) <= int(other.x) <= int(self.x+1) and int(self.y-1) <= int(other.y) <= int(self.y+1): return True
        return False

    def collision(self,b):
        a = self
        if self == b:
            a.xs = -a.xs ; a.ys = -a.ys
            b.xs = -b.xs ; b.ys = -b.ys

    def update(self):
        self.x += self.xs
        self.y += self.ys
        if self.x < 10 or self.x >= self.max_x-10: self.xs = -self.xs
        if self.y < 10 or self.y >= self.max_y-10: self.ys = -self.ys
        return int(self.x),int(self.y)

def balls_app():
    balls = [Ball()for i in range(15)]
    collision = []

    for i, b in enumerate(balls): # possible collision (avoid duplicates)
        for s in balls[i + 1:]:
            collision.append([b,s])

    while True:
        for b in balls:
            t.fillrect((int(b.x), int(b.y)), (3, 3),0)
            x, y = b.update()
            t.fillrect((x, y), (3, 3),b.color)
        for a,b in collision: a.collision(b)
        if sw() or click: return True

#########################################################################################################

reordered = b''
def bouncing_logo_app():
    global reordered
    gc.collect()
    if reordered == b'':
        bmp = open('ST_40.bmp','rb')
        data = bmp.read(54)
        bm,file_size,x1,x2,h54,h40,w,h,layers,bits_per_pixel,compression ,x3,res_h,res_v,x7,x8 = struct.unpack("<HLHHLLLLHHLLLLLL", data[:54])
        assert bm == 0x4D42, "bad header 1"
        assert h54 == 54, "bad header 2"
        assert h40 == 40, "bad header 3"
        assert layers == 1, "bad header 4"
        assert bits_per_pixel == 24, "bad header 6"
        assert compression == 0, "bad header 7"

        line_size_in_bytes = bits_per_pixel * w//8
        lines = bmp.read() # read all data as bytes

        all_pixels = [ (TFTColor(lines[i*3+2],lines[i*3+1],lines[i*3])) for i in range(w*h) ] # generate pixels
        del lines
        all_pixels = struct.pack( '>%dH' % (w*h), *all_pixels) # pack as bytearray of RGB565
         # swap verticaly lines for LCD
        for y in range(h):
            reordered += all_pixels[(h-y)*w*2:(h-y+1)*w*2]
        del  all_pixels
        gc.collect()
    else:
        bmp = open('ST_40.bmp','rb')
        data = bmp.read(54)
        bm,file_size,x1,x2,h54,h40,w,h,layers,bits_per_pixel,compression ,x3,res_h,res_v,x7,x8 = struct.unpack("<HLHHLLLLHHLLLLLL", data[:54])
    i,j = (randint(0,20),randint(0,20)) # random pos and move
    inc_i = randint(5,9)/16
    inc_j = randint(5,9)/16
    
    bg = 0xFFFF
    t.fill(bg)
    while True:
        t.image( int(i),int(j),
                 int(w-1+0+i),int(h-1+j),
                 reordered)
        t.rect((int(i)-1,int(j)-1),(w+2,h+2),bg) # cleanup border
        i += inc_i
        j += inc_j
        if i >= 128-w or i <= 1:
            inc_i = - inc_i
        if j >= 128-h or j <= 1:
            inc_j = - inc_j
        pyb.delay(5)
        if sw() or click:
            gc.collect()
            return True

#########################################################################################################

MAX_ITER = const(100)
WIDTH = const(128)
HEIGHT = const(128) 
RE_START = const(-2)
RE_END = const(1)
IM_START = -1.5
IM_END = 1.5

@micropython.native
def mandelbrot(c):
    z = 0
    n = 0
    while abs(z) <= 2 and n < MAX_ITER:
        z = z*z + c
        n += 1 
    return n 
  
@micropython.native
def hsv_to_rgb(h, s, v):
    if s == 0.0: v*=255; return (v, v, v)
    i = int(h*6.) 
    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

def mandel_app():
    t0 = time.time()
    for x in range(0, WIDTH):
        for y in range(0, HEIGHT):
            c = complex(RE_START + (x / WIDTH) * (RE_END - RE_START), IM_START + (y / HEIGHT) * (IM_END - IM_START)) # Convert pixel coordinate to complex number
            m = mandelbrot(c)             # Compute the number of iterations
            hue = m/255 # The color depends on the number of iterations
            saturation = 1
            value = 1 if m < MAX_ITER else 0
            r,g,b= hsv_to_rgb(hue,saturation,value) # Plot the point
            color = TFTColor(r,g,b)
            t.pixel((x,y),color)
            if sw() or click: return True
            
    while True:
        time.sleep(0.2)
        if sw() or click: return True

#########################################################################################################

def meteo_app():
    pos1 = (15,5)
    pos2 = (10,30)
    pos3 = (25,45)
    last_temp = last_press = last_alt = 0
    t0 = time.ticks_ms()
    idx = 0
    while True:
        if sw() or click: return True
        time.sleep(0.3)
        refresh = (time.ticks_ms() - t0) > 2000
        
        temp,press = lps22.get()
        altitude = abs(lps22.altitude())
        print('temp: %s' % temp)
        
        if abs(last_temp - temp) > 0.2 or refresh:
            last_temp = temp
            stemp = '%2.1fC' % temp    
            t.fillrect(pos1,(96,28),TFT.BLACK)
            t.text(pos1,stemp,TFT.WHITE,terminalfont,3)
        
        if abs(last_press - press) > 0.2 or refresh:
            last_press = press
            spress = '%2.1fmB' % press
            t.fillrect(pos2,(96,16),TFT.BLACK)
            t.text(pos2,spress,TFT.GRAY,terminalfont,2)

        if abs(last_alt - altitude) > 0.5 or refresh:
            last_alt = altitude
            saltitude = '%2.1fm' % altitude
            t.fillrect(pos3,(96,16),TFT.BLACK)
            t.text(pos3,saltitude,TFT.GRAY,terminalfont,2)

        if idx == 0:
            t.fillrect((0,64),(128,64),TFT.BLACK)
        temp_color = TFTColor(255,0,0)
        if temp < 30: temp_color = TFTColor(0,200,0)
        if temp < 20: temp_color = TFTColor(0,0,255)

        idx = (idx+1)%128
        y = 128-int(temp)*2
        t.fillrect((idx,y),(2,2),temp_color)
       
        if refresh: t0 = time.ticks_ms()        

#########################################################################################################

def rect_fall_app():
    t.fill(0)
    t.setvscroll(2,2)
    i = 0
    while True:
        x,y = randint(1,110),randint(1,110)
        w,h = randint(2,50),randint(2,50)
        r,g,b = randint(128,255),randint(128,255),randint(128,255)
        t.fillrect((x,y),(w,h),TFTColor(r,g,b))
        t.vscroll(i)
        i = (i+1)%128
        time.sleep(0.020)
        if sw() or click: break
    t.vscroll(0)

#########################################################################################################

def reveil_app():
    global click
    SET_NONE = 0
    SET_HOUR = 1
    SET_MINUTE = 2
    SET_YEAR  = 3
    SET_MONTH = 4
    SET_DAY = 5
    last_pos = e.position
    set_x = 0
    r = RTC()
    Y,M,D,tz,h,m,s,xx = r.datetime()
    last_hms = 0,0,0
    while True:
        pos = e.position
        Y,M,D,tz,h,m,s,xx = r.datetime()
        if click:
            set_x = (set_x + 1) % 6
            click = False
        if pos != last_pos:
            inc = 1 if pos < last_pos else -1
            if set_x == SET_HOUR: h = (h + inc) % 24
            elif set_x == SET_MINUTE: m = (m + inc) % 60
            elif set_x == SET_YEAR: Y = (Y + inc)
            elif set_x == SET_MONTH: M = (M + inc)
            if M == 13: M = 1
            if M == 0: M = 12
            Dmax = 31 if M in [1,3,5,7,8,10,12] else 30
            if M == 2: Dmax = 29
            elif set_x == SET_DAY: D = (D + inc)
            if D == Dmax+1: D = 1
            if D == 0: D = Dmax
            
            last_pos = pos
            r.datetime((Y,M,D,tz,h,m,s,xx))
                
        if last_hms[:-2] != (Y,M,D,tz,h,m):
            last_hms = (Y,M,D,tz,h,m,s,xx)
            t.fill(0)
            t.text((1,30),"%02d:%02d" % (h,m),0xFFFF,terminalfont,4)
            t.text((30,68),"%02d/%02d/%04d" % (D,M,Y),0xFFFF,terminalfont,1)
            print(h,m,s)
            print(D,M,Y)
            update = True

        if last_hms[-2] != (s) or update:
            msg = "           "
            if set_x == SET_HOUR: msg = "heures..."
            if set_x == SET_MINUTE: msg = "minutes..."
            if set_x == SET_YEAR: msg = "annee..."
            if set_x == SET_MONTH: msg = "mois..."
            if set_x == SET_DAY: msg = "jour..."
            
            t.text((2,2),msg,TFT.YELLOW,terminalfont,1)
            t.fillrect((4,62),(2*s,2),0xF000)
            update = False
            
        if sw() :
            e.position = 0
            return True

#########################################################################################################

SCR_SCALE = 4
class Snake:
    LEFT =  1
    RIGHT = 2
    DOWN =  3
    UP =    4
    DIRECTIONS = [UP,LEFT,RIGHT,DOWN]
    MIAMS = 10

    XMAX = 128 // SCR_SCALE + 1 
    YMAX = 128 // SCR_SCALE + 1

    def __init__(self,x=2,y=5):
        self.init(x,y)

    def init(self,x,y):
        self.body = [(x,y),(x+1,y),(x+2,y),(x+3,y)]
        self.last_direction = self.RIGHT
        self.miam = [(randint(1,self.XMAX),randint(1,self.YMAX)) for i in range(self.MIAMS)]
        t.fill(0) # clear

    def check(self):
        x,y = self.body[-1]
        try:
            for pos in self.body[:-2]:
                assert pos != (x,y), 'Cannibal !'
            assert 0 <= x <= self.XMAX, "PAF"
            assert 0 <= y <= self.YMAX, "POUF"
        except Exception as e:
            t.text((20,20),str(e), 0xFFFF,terminalfont,1)
            delay(1000)
            t.fill(0)
            return -1

        if (x,y) in self.miam:
            miam = None
            while miam in [None] + self.body + [self.miam] + [(0,0),(0,1),(0,2)]:
                miam = (randint(2,self.XMAX-1),randint(2,self.YMAX-1))
            self.miam.append(miam)
            self.miam.remove((x,y))
            return 1
        return False

    def move(self,direction,draw=True,debug=False):
        for x,y in self.miam:
            t.fillrect((x * SCR_SCALE, y * SCR_SCALE), (SCR_SCALE, SCR_SCALE), 0xFFFF)

        t.fillrect((5, 5), (10, 10), 0)
        t.text((5,5),str(len(self.body)-4),0xFF00,terminalfont,1)

        x,y = self.body[-1] # get head
        if direction not in self.DIRECTIONS: direction = self.last_direction # last direction as last
        if direction == self.UP:   self.body.append((x,y-1))
        if direction == self.DOWN: self.body.append((x,y+1))
        if direction == self.LEFT: self.body.append((x-1,y))
        if direction == self.RIGHT: self.body.append((x+1,y))
        self.last_direction = direction

        if draw: # body
            t.rect((0,1),(128,128),TFT.BLUE)
            for pos in self.body:
                t.fillrect((x*SCR_SCALE, y*SCR_SCALE), (SCR_SCALE, SCR_SCALE), 0x0FF0)
            x,y = self.body[0]
            t.fillrect((x*SCR_SCALE,y*SCR_SCALE),(SCR_SCALE,SCR_SCALE),0x0)
            
        c = self.check()
        if c == 0: self.body.pop(0)
        elif c == 1:  pass # nothing
        elif c == -1: return True # dead
        return False

def snake_app():
    directions = [ Snake.RIGHT, Snake.DOWN,Snake.LEFT,Snake.UP]
    while True:
        e.position = 0
        s = Snake()
        while True:
            if s.move(direction = directions[e.position % len(directions)]): break
            delay(150)
            if sw() or click: break
        if sw() or click: break
    
    
#########################################################################################################
DICE = [
    [(2,2)], # 1
    [(1,1),(3,3)], # 2
    [(1,1),(3,3),(2,2)], # 3
    [(1,1),(3,3),(1,3),(3,1)], # 4
    [(1,1),(3,3),(1,3),(3,1),(2,2)], # 5
    [(1,1),(1,2),(1,3),(3,1),(3,2),(3,3)], # 6
    ]
        
def dice():
    t.fill(0)
    i = randint(0,5)
    for x,y in DICE[i]:    
        offset = 25
        scale = 40
        size = 16
        t.fillcircle((offset+scale*(x-1),offset+scale*(y-1)),size,0xFFFF)
        
def dice_app():
    T = 20
    while True:
        x,y,z = acc.filtered_xyz()
        for i in range(5):
            dice()
            delay(150)
                
        t.rect((1,1),(127,127),0xF000)
        t.rect((2,2),(125,125),0xF000)
        while abs(y) < T and abs(z) < T:
            x,y,z = acc.filtered_xyz()
            delay(100)
            if sw() or click: return
            
def pong_app():
    # Dimensions et position de la raquette: Longueur, hauteur, position X,Y
    raquetteL = 4
    raquetteH = 10
    raquetteX = 1
    raquetteY = 60
    raquetteVitesse = 4
    last_posR = e.position

    # Dimensions et position de la balle: Longeur, hauteur, position X,Y
    balleR = 3
    balleX = randint(40,80)
    balleY = randint(40,80)

    # Zone de rebond de la balle
    zoneXLow  = raquetteL+balleR
    zoneXHigh = 128 - balleR
    zoneYLow  = balleR
    zoneYHigh = 128 - balleR
    
    # Sens de déplacement de la balle 
    balleMoveX = balleMoveY = 1
    
    # Nombre de touches de balle 
    scoreOK = scoreKO = 0
    
    raquetteCouleur = TFT.WHITE

    t.fill(0) # Ecran noir
    update_score = True
    while True:
        # Gestion de la raquette 
        posR = e.position
        if posR != last_posR: # La raquette a bougé 
            last_posR = posR 
            t.fillrect((1,1),(10,128),TFT.BLACK) # On efface toute la ligne de la raquette en couleur de fond 
            inc = raquetteVitesse if e.forward else -raquetteVitesse
            if 0 <= raquetteY+inc <= 128 - raquetteH: raquetteY += inc
        t.fillrect((raquetteX,raquetteY),(raquetteL,raquetteH),raquetteCouleur) # Affichage de la raquette
            
        if update_score: # Affichage score ou autres donnees 
            t.fillrect((100,28),(6,80),TFT.BLACK) # on efface
            t.text((100,28),'%d' % scoreOK,TFT.GREEN,terminalfont,1)
            t.text((100,100),'%d' % scoreKO,TFT.RED,terminalfont,1)
            update_score = False

        # Gestion de la balle
        t.fillcircle((balleX,balleY),balleR,TFT.BLACK) # On efface la balle d'avant
        balleX = balleX + balleMoveX
        balleY = balleY + balleMoveY
        t.fillcircle((balleX,balleY),balleR,TFT.YELLOW)
        
        if 100 - balleR <= balleX <= 105 + balleR: update_score = True # La balle passe sur le score
        
        if balleX >= zoneXHigh: # On atteint la limite supérieure en X: on change de sens 
            balleMoveX = -balleMoveX
        elif balleX <= zoneXLow:
            balleMoveX = randint(1,2) # nouvelle vitesse de balle 
            update_score = True # le score va changer
            # On a atteint la bas de l'écran. Il faut donc voir si la requette est là...
            if raquetteY - balleR <= balleY <= raquetteY + raquetteH + balleR:
                scoreOK += 1 # La balle est sur la raquette
                raquetteCouleur = TFT.GREEN
            else:
                scoreKO += 1 # La balle a raté la raquette
                raquetteCouleur = TFT.RED
                
        if balleY >= zoneYHigh or balleY <= zoneYLow: # On atteint les limites Y: on change de sens
            balleMoveY = -balleMoveY
            
        time.sleep(0.005)
        if sw() or click: break

#########################################################################################################
        
click = False
last_click = 0
def clicked(a):
    global click, last_click
    t = time.ticks_ms()
    if t - last_click < 500: return
    last_click = t
    click = True
    
pin_vpp = Pin('X4',Pin.OUT)
pin_vpp.value(1)
e = Encoder(Pin('X1',Pin.IN,Pin.PULL_NONE),Pin('X2',Pin.IN,Pin.PULL_NONE),Pin('X3',Pin.PULL_NONE),clicked)
#e = Encoder(Pin('X1',Pin.IN,Pin.PULL_UP),Pin('X2',Pin.IN,Pin.PULL_UP),Pin('X3',Pin.PULL_NONE),clicked)

APPS = [
    ("ST logo",bouncing_logo_app),
    ("Heure", reveil_app),
    ("Meteo",meteo_app),
    ("Niveau",level_sensors_app),
    ("Mandelbrot",mandel_app),
    ("Bouncing Balls",balls_app),
    ("Snake",snake_app),
    ("Dice",dice_app),
    ("Pong",pong_app),
    ("Rect. Falls",rect_fall_app),    ]

def app_menu():
    global click
    global last_pos
    t.fill(0)
    scale = 1
    Y0 = 40
    X0 = 20 ; X1 = 4 ; sel = ">"
    H = 9*scale
    y = Y0 ; x = X0
    t.text((X0,Y0-20),"MENU",0x001F,terminalfont,2)
    t.rect((X0-3,Y0-23),(80,20),0x001F)
    for name,func in APPS:
        t.text((x,y),name,0xFFFF,terminalfont,scale)
        y += H
    
    last_pos = e.position % len(APPS)
    pos = 0
    init = True
    while not click:
        pos = e.position % len(APPS)
        if pos != last_pos or init:
            init = False
            t.text((x,Y0+H*last_pos),APPS[last_pos][0],0xFFFF,terminalfont,scale)
            t.text((x,Y0+H*pos),APPS[pos][0],0xF000,terminalfont,scale)
            last_pos = pos
        time.sleep_ms(100)
    click = False
    t.fill(0)
    return APPS[pos][1]

#########################################################################################################
if 1:
  while True:
    func = app_menu()
    pos = e.position
    func()
    gc.collect()
    e.position = pos
    click = False
