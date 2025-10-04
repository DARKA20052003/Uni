class Fraccion:
  def __init__(self, numerador, denominador):
    self.numerador=int(numerador)
    self.denominador=int(denominador)
  def sumar (self, fraccion2):
    resultadoNumerador=(self.numerador * fraccion2.denominador)+(fraccion2.numerador * self.denominador)
    resultadoDenominador=self.denominador * fraccion2.denominador
    return Fraccion(resultadoNumerador, resultadoDenominador)
  '''def mostrarFraccion(self):
    print(f"{self.numerador}/{self.denominador}")'''
  def __add__(self, fraccion2):
    numNuevo=(self.numerador * fraccion2.denominador)+(fraccion2.numerador * self.denominador)
    denomNuevo=self.denominador * fraccion2.denominador
    return Fraccion(numNuevo, denomNuevo)
  def __str__(self):
    return f"{self.numerador}/{self.denominador}"