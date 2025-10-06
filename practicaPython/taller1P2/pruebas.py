from claseCoche import Coche
from claseCuentaBancaria import CuentaBancaria
from claseEstudianteTaller import Estudiante
from claseRectangulo import Rectangulo

#Prueba de coches
carro1=Coche('Honda','Civic Coupé', '1972')
carro2=Coche('Ford', 'Mustang', '1969')
carro3=Coche('Tesla', 'Model 3', '2023')

carro1.mostrarInfo()
carro2.mostrarInfo()
carro3.mostrarInfo()

#Prueba de cuentas bancarias
cuenta1 = CuentaBancaria('Andrés David Darquea Alcívar', 100)
cuenta2 = CuentaBancaria('Cindy Vanessa Alcívar Murillo', 326)

cuenta1.mostrarSaldo()
cuenta1.retirar(50)
cuenta1.mostrarSaldo()

cuenta2.retirar(327)
cuenta2.retirar(30)
cuenta2.mostrarSaldo()
cuenta2.retirar(300)
cuenta2.mostrarSaldo()

#Pruebas de estudiantes
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

#Prueba de rectangulos
r1=Rectangulo(12, 24)
r2=Rectangulo(10, 5)

r1.area()
r1.perimetro()

r2.area()
r2.perimetro()