'''Programación orientada a objetos, paradigma de programación que utiliza objetos y clases para organizar el código. 
Abstracción: Se usa para el análisis de la estructura del problema, ocultando detalles innecesarios y enfocándose en lo esencial.
   - Clase: Es una plantilla o molde para crear objetos, wue define métodos y atributos para reutilizar en instancias(Una función como tal).
   - Objeto: Es una instancia de una clase, que contiene datos y métodos definidos en la clase(Objeto que obedece a la clase).
   - Atributo: Es una variable que pertenece a una clase y define las características del objeto(¿Característica del objeto o clase?).
   - Método: Es una función definida dentro de una clase que define el comportamiento del objeto(¿Qué hace?).
Sintaxis básica para crear una clase e instanciar un objeto:
1. Crear una clase.'''
class Persona: #Class es keyword de Python para crear clases y la primera letra de la clase debe ser mayus
    #Toda clase tiene un inicializador o builder.
    cantidadDePiernas=2 #Atributo de clase.
    def __init__(self, nombre, edad, ci): #Inicializador o builder de clase __init__, se colocan los parámetros de los atributos de objeto entre paréntesis, después de self.
        self.nombre=nombre #Los atributos se especifican al lado de self
        self.edad=edad
        self.anoDeNacimiento=2025-int(edad) #Ejemplo de atributo que usa un parámetro
        self.cedulaDeIdentidad=ci
    def actualizarCI(self, nuevaCI):
        self.ci=nuevaCI
