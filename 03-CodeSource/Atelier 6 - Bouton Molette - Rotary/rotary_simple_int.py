# main.py -- put your code here!
from machine import Pin

global cur_position, pin_x

def y_callback(line):
    global pin_x, cur_position
    if pin_x.value() == 0:
        # x = 0 => on tourne dans le sens des aiguilles d'une montre
        cur_position += 1
    else:
        # x = 1 => on tourne dans le sens inverse des aiguilles d'une montre
        cur_position -= 1

def k_callback(line):
    global cur_position
    # on veut reinitialiser la position quand on appuie sur le bouton
    cur_position = 0
        
# on alimente le bouton molette
pin_vpp = Pin('X4',Pin.OUT)
pin_vpp.value(1)

pin_x = Pin('X1')
pin_y = Pin('X2')

# Derniere position
last_position = 0
cur_position = 0
print(cur_position)

# enregistrement de la "callback" appelee sur front descendant de Y
pin_y.irq(trigger=Pin.IRQ_FALLING, handler=y_callback)

# optionnel si on veut reinitialiser la position quand on appuie sur le bouton
pin_key = Pin('X3')
pin_key.irq(trigger = Pin.IRQ_FALLING, handler=k_callback)

while True:
    # si la position a change dans une callback
    if (last_position != cur_position):
        print(cur_position)
        # et on memorise la derniere poition (= la nouvelle "courante")
        last_position = cur_position

