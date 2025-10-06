'''Crea una clase rectangulo con:
    - Atributos: Alto, Ancho.
    - Método área, que calcule y retorne el área.
    - Método perímetro, que calcule y retorne el perímetro.
'''
class Rectangulo:
    def __init__(self, alto, ancho):
        self.alto=alto
        self.ancho=ancho
    
    def area(self):
        print (self.ancho * self.alto)
    
    def perimetro(self):
        print (2*(self.alto + self.ancho))

