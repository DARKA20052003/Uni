import numpy as np
import matplotlib
# Intentar usar un backend interactivo disponible
backends_disponibles = ['Qt5Agg', 'Qt4Agg', 'GTKAgg', 'WXAgg']
backend_usado = None
for backend in backends_disponibles:
    try:
        matplotlib.use(backend)
        backend_usado = backend
        break
    except:
        continue

if not backend_usado:
    # Fallback a Agg (no-interactivo pero funcional)
    matplotlib.use('Agg')
    
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib.patches as patches


class BrazoRobotico2DOF:
    """
    Clase para representar un brazo robótico de 2 grados de libertad.
    Calcula la cinemática directa (posición del efector final).
    
    Para un brazo 2DOF en el plano XY:
    x = L1*cos(θ1) + L2*cos(θ1+θ2)
    y = L1*sin(θ1) + L2*sin(θ1+θ2)
    """
    
    def __init__(self, L1=1.5, L2=1.0, theta1_inicial=0, theta2_inicial=0):
        """
        Inicializa el brazo robótico 2DOF.
        
        Args:
            L1: Longitud del primer eslabón
            L2: Longitud del segundo eslabón
            theta1_inicial: Ángulo inicial de la primera articulación (radianes)
            theta2_inicial: Ángulo inicial de la segunda articulación (radianes)
        """
        self.L1 = L1
        self.L2 = L2
        self.theta1 = theta1_inicial
        self.theta2 = theta2_inicial
        
    def cinematica_directa(self, theta1, theta2):
        """
        Calcula la posición del efector final usando cinemática directa.
        
        Args:
            theta1: Ángulo de la primera articulación (radianes)
            theta2: Ángulo de la segunda articulación (radianes)
            
        Returns:
            Tupla (x, y) con las coordenadas del efector final
        """
        self.theta1 = theta1
        self.theta2 = theta2
        
        # Posición del efector final
        x = self.L1 * np.cos(theta1) + self.L2 * np.cos(theta1 + theta2)
        y = self.L1 * np.sin(theta1) + self.L2 * np.sin(theta1 + theta2)
        
        return x, y
    
    def obtener_articulos(self, theta1, theta2):
        """
        Retorna las posiciones de las articulaciones para dibujar.
        
        Args:
            theta1: Ángulo de la primera articulación (radianes)
            theta2: Ángulo de la segunda articulación (radianes)
            
        Returns:
            Tupla con (coordenadas_x, coordenadas_y, posicion_articulo2)
        """
        # Posición de la primera articulación (base)
        x_articulo1 = 0
        y_articulo1 = 0
        
        # Posición de la segunda articulación (fin del primer eslabón)
        x_articulo2 = self.L1 * np.cos(theta1)
        y_articulo2 = self.L1 * np.sin(theta1)
        
        # Posición del efector final (fin del segundo eslabón)
        x_efector, y_efector = self.cinematica_directa(theta1, theta2)
        
        # Coordenadas para dibujar los eslabones
        x_coords = [x_articulo1, x_articulo2, x_efector]
        y_coords = [y_articulo1, y_articulo2, y_efector]
        
        return x_coords, y_coords, (x_articulo2, y_articulo2)
    
    def obtener_longitud_alcance(self):
        """Retorna la longitud máxima de alcance del brazo."""
        return self.L1 + self.L2
    
    def obtener_matriz_homogenea_completa(self, theta1, theta2):
        """
        Retorna la matriz de transformación completa considerando ambas articulaciones.
        
        Args:
            theta1: Ángulo de la primera articulación (radianes)
            theta2: Ángulo de la segunda articulación (radianes)
            
        Returns:
            Matriz 3x3 de transformación homogénea final
        """
        # Ángulo final acumulado
        theta_final = theta1 + theta2
        x_final, y_final = self.cinematica_directa(theta1, theta2)
        
        # Matriz de transformación homogénea
        T = np.array([
            [np.cos(theta_final), -np.sin(theta_final), x_final],
            [np.sin(theta_final), np.cos(theta_final), y_final],
            [0, 0, 1]
        ])
        return T


def crear_dashboard_2dof():
    """
    Crea un dashboard interactivo para visualizar la cinemática directa de 2DOF.
    """
    # Crear instancia del brazo
    brazo = BrazoRobotico2DOF(L1=1.5, L2=1.0, theta1_inicial=0, theta2_inicial=0)
    
    # Crear figura y subplots
    fig = plt.figure(figsize=(15, 7))
    fig.suptitle('Dashboard - Cinemática Directa (2 DOF)', fontsize=16, fontweight='bold')
    
    # Subplot 1: Visualización del brazo
    ax1 = plt.subplot(1, 2, 1)
    alcance_max = brazo.obtener_longitud_alcance()
    ax1.set_xlim(-alcance_max - 0.5, alcance_max + 0.5)
    ax1.set_ylim(-alcance_max - 0.5, alcance_max + 0.5)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('X (unidades)', fontsize=10)
    ax1.set_ylabel('Y (unidades)', fontsize=10)
    ax1.set_title('Posición del Brazo Robótico 2DOF', fontsize=12, fontweight='bold')
    
    # Dibujar el plano de referencia
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=0, color='k', linewidth=0.5)
    
    # Elementos para los eslabones
    linea_eslabon1, = ax1.plot([], [], 'b-', linewidth=4, label='Eslabón 1', alpha=0.7)
    linea_eslabon2, = ax1.plot([], [], 'c-', linewidth=3, label='Eslabón 2', alpha=0.7)
    punto_base, = ax1.plot([0], [0], 'go', markersize=12, label='Base', zorder=5)
    punto_articulo2, = ax1.plot([], [], 'yo', markersize=10, label='Articulación 2', zorder=5)
    punto_efector, = ax1.plot([], [], 'r*', markersize=25, label='Efector Final', zorder=5)
    
    # Círculos que muestran el rango de movimiento
    circulo_interno = patches.Circle((0, 0), brazo.L1 - brazo.L2, fill=False, 
                                     edgecolor='gray', linestyle=':', 
                                     linewidth=1, alpha=0.3)
    circulo_externo = patches.Circle((0, 0), alcance_max, fill=False, 
                                     edgecolor='gray', linestyle='--', 
                                     linewidth=1, alpha=0.5)
    ax1.add_patch(circulo_interno)
    ax1.add_patch(circulo_externo)
    ax1.legend(loc='upper right', fontsize=9)
    
    # Subplot 2: Información del sistema
    ax2 = plt.subplot(2, 2, 2)
    ax2.axis('off')
    info_text = ax2.text(0.05, 0.95, '', transform=ax2.transAxes, 
                         fontsize=10, verticalalignment='top',
                         family='monospace', bbox=dict(boxstyle='round', 
                         facecolor='wheat', alpha=0.5))
    
    # Subplot 3: Gráfico de trayectoria
    ax3 = plt.subplot(2, 2, 4)
    ax3.set_xlabel('θ1 (radianes)', fontsize=10)
    ax3.set_ylabel('Posición del Efector (unidades)', fontsize=10)
    ax3.set_title('Posición vs Ángulos', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Líneas para mostrar posición actual
    linea_x_actual, = ax3.plot([], [], 'b--', linewidth=2, alpha=0.7, label='X actual')
    linea_y_actual, = ax3.plot([], [], 'r--', linewidth=2, alpha=0.7, label='Y actual')
    punto_x_actual, = ax3.plot([], [], 'bo', markersize=8)
    punto_y_actual, = ax3.plot([], [], 'ro', markersize=8)
    ax3.legend(fontsize=9)
    
    # Sliders para los ángulos
    ax_slider1 = plt.axes([0.15, 0.12, 0.3, 0.02])
    ax_slider2 = plt.axes([0.15, 0.08, 0.3, 0.02])
    
    slider_theta1 = Slider(ax_slider1, 'θ1 (rad)', 0, 2*np.pi, 
                           valinit=0, color='blue', alpha=0.7)
    slider_theta2 = Slider(ax_slider2, 'θ2 (rad)', -np.pi, np.pi, 
                           valinit=0, color='cyan', alpha=0.7)
    
    # Datos para gráfico de trayectoria
    theta1_range = np.linspace(0, 2*np.pi, 100)
    
    def actualizar(val):
        """Actualiza la visualización cuando cambian los ángulos."""
        theta1 = slider_theta1.val
        theta2 = slider_theta2.val
        
        # Obtener posiciones de articulaciones
        x_coords, y_coords, pos_art2 = brazo.obtener_articulos(theta1, theta2)
        
        # Actualizar eslabones
        linea_eslabon1.set_data([x_coords[0], x_coords[1]], 
                                [y_coords[0], y_coords[1]])
        linea_eslabon2.set_data([x_coords[1], x_coords[2]], 
                                [y_coords[1], y_coords[2]])
        
        # Actualizar puntos
        punto_articulo2.set_data([pos_art2[0]], [pos_art2[1]])
        punto_efector.set_data([x_coords[2]], [y_coords[2]])
        
        # Calcular distancia y ángulo del efector
        r_efector = np.sqrt(x_coords[2]**2 + y_coords[2]**2)
        angulo_efector = np.arctan2(y_coords[2], x_coords[2])
        
        # Actualizar información
        info_str = f"""
PARÁMETROS DEL SISTEMA
──────────────────────────────
L1:               {brazo.L1:.4f} unidades
L2:               {brazo.L2:.4f} unidades
θ1:               {np.degrees(theta1):7.2f}° ({theta1:.4f} rad)
θ2:               {np.degrees(theta2):7.2f}° ({theta2:.4f} rad)
θ_total:          {np.degrees(theta1+theta2):7.2f}°

POSICIÓN DEL EFECTOR FINAL
──────────────────────────────
X:                {x_coords[2]:7.4f} unidades
Y:                {y_coords[2]:7.4f} unidades
Distancia (r):    {r_efector:.4f} unidades
Ángulo (atan2):   {np.degrees(angulo_efector):7.2f}°

POSICIÓN ARTICULACIÓN 2
──────────────────────────────
X:                {pos_art2[0]:7.4f} unidades
Y:                {pos_art2[1]:7.4f} unidades

ALCANCE
──────────────────────────────
Máximo:           {brazo.obtener_longitud_alcance():.4f} unidades
Mínimo:           {abs(brazo.L1 - brazo.L2):.4f} unidades
"""
        info_text.set_text(info_str)
        
        # Actualizar gráfico de trayectoria
        x_tray = []
        y_tray = []
        for t1 in theta1_range:
            x, y = brazo.cinematica_directa(t1, theta2)
            x_tray.append(x)
            y_tray.append(y)
        
        # Limpiar y redibujar
        ax3.clear()
        ax3.plot(theta1_range, x_tray, 'b-', linewidth=2, label='X', alpha=0.6)
        ax3.plot(theta1_range, y_tray, 'r-', linewidth=2, label='Y', alpha=0.6)
        ax3.axvline(x=theta1, color='g', linestyle='--', linewidth=1.5, alpha=0.7)
        ax3.plot(theta1, x_coords[2], 'bo', markersize=8)
        ax3.plot(theta1, y_coords[2], 'ro', markersize=8)
        ax3.grid(True, alpha=0.3)
        ax3.set_xlabel('θ1 (radianes)', fontsize=10)
        ax3.set_ylabel('Posición del Efector (unidades)', fontsize=10)
        ax3.set_title('Posición vs θ1 (θ2 fijo)', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.set_xlim(0, 2*np.pi)
        
        fig.canvas.draw_idle()
    
    # Conectar los sliders con la función de actualización
    slider_theta1.on_changed(actualizar)
    slider_theta2.on_changed(actualizar)
    
    # Actualización inicial
    actualizar(0)
    
    plt.subplots_adjust(left=0.1, right=0.95, top=0.93, bottom=0.2, hspace=0.4, wspace=0.3)
    plt.show()


if __name__ == "__main__":
    print("=" * 70)
    print("DASHBOARD DE CINEMÁTICA DIRECTA - 2 DOF (BRAZO DE 2 ESLABONES)")
    print("=" * 70)
    print("\nIniciando dashboard interactivo...")
    print("\nCaracterísticas:")
    print("  - Brazo con 2 eslabones en el plano XY")
    print("  - Cinemática Directa:")
    print("    x = L1·cos(θ1) + L2·cos(θ1+θ2)")
    print("    y = L1·sin(θ1) + L2·sin(θ1+θ2)")
    print("\nControles:")
    print("  - Slider θ1: Controla el ángulo de la primera articulación (0 a 2π)")
    print("  - Slider θ2: Controla el ángulo de la segunda articulación (-π a π)")
    print("\nVisualización:")
    print("  - Panel izquierdo: Posición del brazo en tiempo real")
    print("  - Panel superior derecho: Información del sistema")
    print("  - Panel inferior derecho: Gráfico de posición vs ángulos")
    print("\n" + "=" * 70 + "\n")
    
    crear_dashboard_2dof()
