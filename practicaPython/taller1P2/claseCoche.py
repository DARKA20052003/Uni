class Coche:
    def __init__(self, marca, modelo, ano):
        self.marca=marca #Asignado el parametro marca al atributo marca.
        self.modelo=modelo #Asignado el parámetro modelo al atributo modelo.
        self.anoDeEstreno=ano #Asignado el parámetro ano al atributo anoDeEstreno.
    def mostrarInfo(self):
        print('-'*30) #Marco para hacer la división entre la info de los coches.
        print(f'Modelo:{self.modelo}\nMarca:{self.marca}\nAño de estreno:{self.anoDeEstreno}.')
        print('-'*30)