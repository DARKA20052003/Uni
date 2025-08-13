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

estudiante1=Estudiante('Andrés David Darquea Alcívar', 22, 'Ingeniería en Software', [8, 9, 7, 8])
estudiante2=Estudiante('Galo Eusebio Enriquez Vera', 19, 'Ingeniería Industrial', [6, 4, 6, 2])

#Primera prueba.
print('*'*50)
print(f'Estudiante: {estudiante1.nombre}\nEdad:{estudiante1.edad}\nCarrera:{estudiante1.carrera}')
estudiante1.aprobo()
print('*'*50)

#Segunda prueba.
print('*'*50)
print(f'Estudiante: {estudiante2.nombre}\nEdad:{estudiante2.edad}\nCarrera:{estudiante2.carrera}')
estudiante2.aprobo()
print('*'*50)