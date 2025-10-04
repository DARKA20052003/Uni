import math
import numpy as np
import matplotlib.pyplot as plt

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
    def __init__(self, elemento):
        self.elemento= np.array(elemento)
    def sumar (self, otroVector):
        return self.elemento + otroVector.elemento
v1=Vector([1,1,1])
v2=Vector([1,2,3])
v3=v1.sumar(v2)
print(v3)

class Funcion:
    def __init__(self, tipo):
        self.tipo=tipo
    def graficar(self):
        x=np.linspace(-10,10,200)
        if self.tipo == 'cuadratica':
            y = x**2
        else:
            y=np.cos(x)
        plt.plot(x,y,label=self.tipo)
        plt.title('Gráfico 22/08')
        plt.show()

g1=Funcion('cuadratica')
g1.graficar()