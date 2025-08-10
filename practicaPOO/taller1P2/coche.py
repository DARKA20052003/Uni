class Coche:
    def __init__(self, marca, modelo, ano):
        self.marca=marca #Asignado el parametro marca al atributo marca.
        self.modelo=modelo #Asignado el parámetro modelo al atributo modelo.
        self.anoDeEstreno=ano #Asignado el parámetro ano al atributo anoDeEstreno.
    def mostrarInfo(self):
        print('-'*30)
        print(f'Modelo:{self.modelo}\nMarca:{self.marca}\nAño de estreno:{self.anoDeEstreno}.')
        print('-'*30)
carro1=Coche('Honda','Civic Coupé', '1972')
carro2=Coche('Ford', 'Mustang', '1969')
carro3=Coche('Tesla', 'Model 3', '2023')

carro1.mostrarInfo()
carro2.mostrarInfo()
carro3.mostrarInfo()