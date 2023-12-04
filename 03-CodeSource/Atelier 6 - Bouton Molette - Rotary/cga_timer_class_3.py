from machine import Pin
from pyb import  Timer

class Encoder:
    def __init__(self, pin_x, pin_y, pin_key=None,key_cb=None):
        self.pin_x = pin_x
        self.pin_y = pin_y
        self.position = 0
        self.last_y = 1
        self.key_cb = key_cb
        self.tim = Timer(4, period=2, callback=self.tim_callback)
		
        if pin_key and key_cb:
            self.k_interrupt = pin_key.irq(trigger = Pin.IRQ_FALLING, handler=self.k_callback)
        
    def tim_callback(self,line):
        cur_x = self.pin_x.value()
        cur_y = self.pin_y.value()
        
        if (self.last_y != cur_y):
            # y a changé
            if cur_y == 0:
                # Front descendant de y 
                if cur_x == 0:
                    # x = 0 => on tourne dans le sens des aiguilles d'une montre
                    self.position += 1
                else:
                    # x = 1 => on tourne dans le sens inverse des aiguilles d'une montre
                    self.position -= 1
    
			self.last_y = cur_y
        
    def k_callback(self, line):
        if self.key_cb:
            self.key_cb(line)
            
def myCallBack(p):
    s.position = 0

pin_vpp = Pin('X4',Pin.OUT)
pin_vpp.value(1)  
s = Encoder(Pin('X1'),Pin('X2'), # ==> signaux roue codeuse
                Pin('X3'),myCallBack)    # ==> signal bouton et sa fonction    
pos = -1
while True:
    if (s.position != pos):
        pos = s.position
        print(s.position)




