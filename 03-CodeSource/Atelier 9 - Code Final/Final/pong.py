import time,math,struct
from ST7735 import *
from machine import Pin, SPI,I2C
from pyb import LED,delay,Accel,ADC,Pin,Timer,Switch,LED

from random import randint
#from rotary import Encoder
from LPS22 import LPS22
from rotary_tim import Encoder

terminalfont={
    "Width":6,"Height":8,
    "Start":32,"End":127,
    "Data":bytearray(open('fnt.bin').read())}

#init devices 
sw = Switch()
acc = Accel()
i2c = I2C(2)
lps22 = LPS22(i2c)
spi = SPI(2, baudrate=60000000, polarity=0, phase=0)
t = TFT(spi, aDC="Y3", aReset="Y4",aCS='Y5')
t.initb2()
t.fill(0)


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

click = False
last_click = 0
def clicked(a):
    global click, last_click
    print('x')
    t = time.ticks_ms()
    if t - last_click < 500: return
    click = True
    
e = Encoder(Pin('X1',Pin.IN,Pin.PULL_UP),Pin('X2',Pin.IN,Pin.PULL_UP),Pin('X3',Pin.PULL_UP),clicked)

pong_app()