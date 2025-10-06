
import tkinter as tk
from tkinter import messagebox
from Ejercicio1.model.claseEstudiante import Estudiante, RegistroEstudiantes
# --- Interfaz gráfica ---
def actualizar_lista():
    lista.delete(0, tk.END)
    for est in registro.estudiantes:
        lista.insert(tk.END, str(est))
def agregar():
    nombre = entry_nombre.get()
    carrera = entry_carrera.get()
    promedio = entry_promedio.get()
    if not nombre or not carrera or not promedio:
        messagebox.showwarning("Campos vacíos", "Completa todos los campos.")
        return
    try:
        promedio_float = float(promedio)
    except ValueError:
        messagebox.showerror("Error", "El promedio debe ser un número.")
        return
    est = Estudiante(nombre, carrera, promedio_float)
    registro.agregar_estudiante(est)
    actualizar_lista()
    entry_nombre.delete(0, tk.END)
    entry_carrera.delete(0, tk.END)
    entry_promedio.delete(0, tk.END)

def mostrar_mejor():
    mejor = registro.estudiante_mejor_promedio()
    if mejor:
        messagebox.showinfo("Mejor promedio", f"{mejor.nombre} ({mejor.carrera}) - {mejor.promedio}")
    else:
        messagebox.showinfo("Mejor promedio", "No hay estudiantes registrados.")


registro = RegistroEstudiantes()

ventana = tk.Tk()
ventana.title("Registro de Estudiantes")

tk.Label(ventana, text="Nombre:").grid(row=0, column=0)
entry_nombre = tk.Entry(ventana)
entry_nombre.grid(row=0, column=1)

tk.Label(ventana, text="Carrera:").grid(row=1, column=0)
entry_carrera = tk.Entry(ventana)
entry_carrera.grid(row=1, column=1)

tk.Label(ventana, text="Promedio:").grid(row=2, column=0)
entry_promedio = tk.Entry(ventana)
entry_promedio.grid(row=2, column=1)

tk.Button(ventana, text="Agregar", command=agregar).grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(ventana, text="Mejor Promedio", command=mostrar_mejor).grid(row=4, column=0, columnspan=2, pady=5)

lista = tk.Listbox(ventana, width=40)
lista.grid(row=5, column=0, columnspan=2, pady=10)
actualizar_lista()

ventana.mainloop()