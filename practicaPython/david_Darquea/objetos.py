from clasePerro import Perro
from clasePersona import Persona

'''2. Instanciar personas'''
persona1=Persona('David',22,1313824045)
persona2=Persona('Marlon',19,1234567890)
persona3=Persona('Tyffany',17,9876543210)
persona4=Persona('Miguel',18,2846791350)
print(persona1.cedulaDeIdentidad)
persona1.actualizarCI(1304875782)
print (persona1.anoDeNacimiento)
print(persona1.cedulaDeIdentidad)

'''3. Instanciar perros'''
perro1=Perro('Corviche')
perro2=Perro('Pelusa')
perro2.ladrar()
perro2.actualizarNombre('Lara')
print (perro2.nombre)