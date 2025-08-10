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
'''2. Instanciar objetos'''
persona1=Persona('David',22,1313824045)
persona2=Persona('Marlon',19,1234567890)
persona3=Persona('Tyffany',17,9876543210)
persona4=Persona('Miguel',18,2846791350)
print(persona1.cedulaDeIdentidad)
persona1.actualizarCI(1304875782)
print (persona1.anoDeNacimiento)
#print(persona1.cedulaDeIdentidad)
