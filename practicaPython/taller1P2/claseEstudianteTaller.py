'''Crea una clase estudiante con:
    - Atributos: nombre, edad, carrera y calificacione (lista de núumeros).
    - Método promedio() que retorne el promedio de las calificaciones.
    - Método aprobo() que retorne True si el promedio el igual o mayor a 7,
    y False en caso contrario.
'''
class Estudiante:
    def __init__(self, nombre, edad, carrera, calificaciones):
        self.nombre=nombre
        self.edad=edad
        self.carrera=carrera
        self.calificaciones=calificaciones
    
    def promedio(self):
        return sum(self.calificaciones) / len(self.calificaciones)
    
    def aprobo(self):
        if self.promedio() >= 7:
            print('Aprobado.')
        else:
            print('Reprobado.')
