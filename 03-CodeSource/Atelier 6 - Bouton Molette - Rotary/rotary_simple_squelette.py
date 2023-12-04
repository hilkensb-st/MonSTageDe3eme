from machine import Pin
from pyb import delay

# on alimente le bouton molette
pin_vpp = Pin('X4',Pin.OUT)
pin_vpp.value(1)

# on cree deux objets associes aux pins X1 et X2
pin_x = Pin('X1')
pin_y = Pin('X2')


# Ajouter votre code maintenant !!!



while True:




    # On pourra lire les valeurs de x et y comme ca:
    nouveau_x = pin_x.value()
    nouveau_y = pin_y.value()
    
    # par ex on peut les afficher mais dans ce cas il faut un petit delai:
    # print(nouveau_x, nouveau_y)
    # delay(100)

