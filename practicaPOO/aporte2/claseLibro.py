'''Crear clase libro con atributos título, autor, año de publicación y precio.
Método mostrar_info() que muestre en pantalla todos los datos del libro de manera ordenada.
Método aplicar_descuento(porcentaje) que reste al precio el porcentaje.
Método es_antiguo() que retorne True si el libro tiene más de 20 años desde su publicación y False en caso contrario.'''
import tkinter as tk

class Libro:
    def __init__(self, titulo, autor, anio_publicacion, precio):
        self.titulo=titulo
        self.autor=autor
        self.anio_publicacion=int(anio_publicacion)
        self.precio=float(precio)
    def mostra_info(self):
        print('*'*30)
        print(f'''Libro:{self.titulo}\nAutor:{self.autor}\nAño de publicación:{self.anio_publicacion}\nPrecio:${self.precio}''')
        print('*'*30)
    def aplicar_descuento(self, porcentaje):
        porcentaje=float(porcentaje)
        descuento=self.precio*porcentaje
        precio_de_descuento=self.precio-descuento
        self.precio=precio_de_descuento
        print(f'El precio de promoción es: ${self.precio-descuento}')
        print('*'*30)
    def es_antiguo(self):
        diferencia=2025-self.anio_publicacion
        if diferencia>20:
            print('El libro es viejo.')
        else:
            print('El libro no es antiguo.')
#Ejemplos
libro1=Libro('100 Años de Soledad','Nosé',1600, 100)
libro1.mostra_info()
libro1.aplicar_descuento(0.3)
libro1.es_antiguo()
libro1.mostra_info()
