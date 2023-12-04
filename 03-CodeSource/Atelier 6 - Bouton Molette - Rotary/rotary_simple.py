from machine import Pin
from pyb import delay

# on alimente le bouton molette
pin_vpp = Pin('X4',Pin.OUT)
pin_vpp.value(1)

# optionnel si on veut reinitialiser le nombre de crans a 0
# quand on appuie sur le bouton
pin_key = Pin('X3')

# on cree deux objets associes aux pins X1 et X2
pin_x = Pin('X1')
pin_y = Pin('X2')

# On initialise le nombre de crans
nouveau_nombre_de_crans = 0
print(nouveau_nombre_de_crans)

nouveau_y = pin_y.value()
    
while True:

    # On memorise les anciens y et nombre de crans
    ancien_nombre_de_crans = nouveau_nombre_de_crans
    ancien_y = nouveau_y

    # On regarde combien vaut y maintenant
    nouveau_y = pin_y.value()

    # si on est passe de ancien y = 1 a nouveau_y = 0
    if (nouveau_y == 0) and (ancien_y == 1):
        x = pin_x.value()
        if x == 0:
            # x = 0 => on tourne dans le sens des aiguilles d'une montre
            nouveau_nombre_de_crans += 1
        else:
            # x = 1 => on tourne dans le sens inverse des aiguilles d'une montre
            nouveau_nombre_de_crans -= 1
    
    # et si on veut reinitialiser le nombre de crans a 0
    # quand on appuie sur le bouton
    if (pin_key.value() == 0):
        nouveau_nombre_de_crans = 0

    # si on a change de nombre de crans, on affiche la valeur
    if (ancien_nombre_de_crans != nouveau_nombre_de_crans):
        print(nouveau_nombre_de_crans)


