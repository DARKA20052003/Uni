'''Crea una clase cuenta bancaria con:
    - Atributos: titular, saldo
    - Método depositar(monto) que sume el 
    monto al saldo.
    - Método retirar(monto) que reste el 
    monto al saldo solo si hay fondos 
    suficientes.
    - Método mostrarSaldo() que imprima el 
    saldo actual.'''
class CuentaBancaria:
    def __init__ (self, titular, saldo):
        self.titular=titular
        self.saldo=saldo
    def depositar(self, monto):
        self.saldo += monto
        print('-'*30)
        print(f'Depósito de ${monto} realizado con éxito.')
        print('-'*30)
    def retirar(self, monto):
        if monto <= self.saldo :
            self.saldo -= monto
            print('-'*30)
            print(f'Retiro de ${monto} realizado con éxito.')
            print('-'*30)
        else:
            print('-'*30)
            print('No hay fondos suficientes.')
            print('-'*30)
    def mostrarSaldo(self):
        print('-'*30)
        print(f'Titular: {self.titular}\nSaldo: ${self.saldo}')
        print('-'*30)

cuenta1 = CuentaBancaria('Andrés David Darquea Alcívar', 100)
cuenta2 = CuentaBancaria('Cindy Vanessa Alcívar Murillo', 326)

cuenta1.mostrarSaldo()
cuenta1.retirar(50)
cuenta1.mostrarSaldo()

cuenta2.retirar(327)
cuenta2.retirar(30)
cuenta2.mostrarSaldo()