# main.py -- put your code here!
from machine import Pin
from pyb import  Timer

global cur_position, pin_x, pin_y, filter_rebund, last_y_level

def timer_callback(timer):
    global state, pin_x, pin_y, cur_position, last_y_level
    # On a terminé le filtrage. Arret du timer
    timer.deinit()   
    state = 0

    # Si Y est à l'état bas et que le dernier niveau de Y etait à 1
    if pin_y.value() == 0:
        if last_y_level == 1:
            if pin_x.value() == 0:
                # x = 0 => on tourne dans le sens des aiguilles d'une montre
                cur_position += 1
            else:
                # x = 1 => on tourne dans le sens inverse des aiguilles d'une montre
                cur_position -= 1

        last_y_level = 0
    else:
        last_y_level = 1

def y_callback(line):
    global state
    print("toto")
    # On vient de recevoir un front descendant ou montant sur le signal Y 
    # Si on n'a pas démarré le timer de filtrage
    if state == 0:
       # lancement du timer de 5ms pour filtrer les rebonds
       Timer(4, period=5, callback=timer_callback)
       # On indique qu'on a démarré le timer pour filtrer tous les prochains fronts
       state = 1


def k_callback(line):
    global cur_position
    # on veut reinitialiser la position quand on appuie sur le bouton
    cur_position = 0
        
# on alimente le bouton molette
pin_vpp = Pin('X4',Pin.OUT)
pin_vpp.value(1)

pin_x = Pin('X1')
pin_y = Pin('X2')
last_y_level = 1
state = 0

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


