import numpy as np
class Vector:
    def __init__(self, elemento):
        self.elemento= np.array(elemento)
    def __add__ (self, otroVector):
        return self.elemento + otroVector.elemento