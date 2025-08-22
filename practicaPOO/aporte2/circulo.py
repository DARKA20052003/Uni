import math
#import numpy
#import matplotlib

class Circulo:
    def __init__(self, radio,):
        self.radio=float(radio)
        self.area=math.pi*(radio**2)
        self.perimetro=math.pi*radio*2
    def mostrar(self):
        print(f'El círculo tiene:\nRadio={self.radio}cm\nArea={self.area}cm^2\nPerimetro={self.perimetro}cm')
    '''def calcular_area(self):
        area=math.pi*(self.radio*self.radio)
        self.area=area
    def calcular_perimetro(self):
        perimetro=math.pi*self.radio*2
        self.perimetro=perimetro'''
#circulo1=Circulo(10)
'''circulo1.calcular_area()
circulo1.calcular_perimetro()'''
#circulo1.mostrar()
class Vector:
    def __init__(self):
        pass