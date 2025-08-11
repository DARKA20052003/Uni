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
        self.saldoOriginal=saldo
    def depositar(self, monto):
        self.saldoNuevo=self.saldoOriginal + monto
        return self.saldoNuevo
    def actualizarSaldo(self):
        self.saldoOriginal=self.saldoNuevo
    def retirar(self, monto):
        if self.saldo > 0:
            self.montoRetirado= self.saldoOriginal - monto
            self.saldoNuevo=self.montoRetirado
            return self.saldoNuevo
        else:
            print('No hay fondos suficientes.')
    def mostrarSaldo(self):
        print(f'Titular: {self.titular}\nSaldo: ${self.saldoNuevo}')

cuenta1 = CuentaBancaria('Andrés David Darquea Alcívar', 100)
cuenta2 = CuentaBancaria('Cindy Vanessa Alcívar Murillo', 326)

cuenta1.mostrarSaldo()
cuenta1.retirar(50)
cuenta1.mostrarSaldo()