import numpy as np
import matplotlib.pyplot as plt

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