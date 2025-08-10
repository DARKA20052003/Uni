class Perro:
    def __init__ (self, nombre):#Inicializa la clase con un parámetro 'nombre'
        self.nombre=nombre #Asigna el atributo nombre al parametro 'nombre'.
    def ladrar(self):
        print(f'{self.nombre}'' dice bark bark!!!')
    def actualizarNombre(self, nuevoNombre):
        nombreViejo=self.nombre
        print(f'{nombreViejo} ahora se llama {nuevoNombre}.')
perro1=Perro('Corviche')
perro2=Perro('Pelusa')
perro2.ladrar()
perro2.actualizarNombre('Lara')