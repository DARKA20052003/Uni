import math
from claseVector import Vector
from claseFuncion import Funcion

class Circulo:
    def __init__(self, radio,):
        self.radio=float(radio)
        self.area=math.pi*(radio**2)
        self.perimetro=math.pi*radio*2
    def mostrar(self):
        print(f'El círculo tiene:\nRadio={self.radio}cm\nArea={self.area}cm^2\nPerimetro={self.perimetro}cm')
    

v1=Vector([1,1,1])
v2=Vector([1,2,3])
v3=v1 + v2
print(v3)

g1=Funcion('cuadratica')
g1.graficar()