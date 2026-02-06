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
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches


class BrazoRobotico1DOF:
    """
    Clase para representar un brazo robótico de 1 grado de libertad.
    Calcula la cinemática directa (posición del efector final).
    """
    
    def __init__(self, longitud_segmento=1.0, angulo_inicial=0):
        """
        Inicializa el brazo robótico.
        
        Args:
            longitud_segmento: Longitud del brazo en unidades
            angulo_inicial: Ángulo inicial en radianes
        """
        self.L = longitud_segmento
        self.theta = angulo_inicial
        
    def cinematica_directa(self, theta):
        """
        Calcula la posición del efector final usando cinemática directa.
        
        Para un brazo de 1 DOF en el plano:
        x = L * cos(theta)
        y = L * sin(theta)
        
        Args:
            theta: Ángulo de la articulación en radianes
            
        Returns:
            Tupla (x, y) con las coordenadas del efector final
        """
        self.theta = theta
        x = self.L * np.cos(theta)
        y = self.L * np.sin(theta)
        return x, y
    
    def obtener_segmentos(self, theta):
        """
        Retorna los segmentos del brazo para dibujar.
        Punto base (0, 0) y punto final (x, y).
        
        Args:
            theta: Ángulo de la articulación en radianes
            
        Returns:
            Tupla con coordenadas x e y del segmento
        """
        x_final, y_final = self.cinematica_directa(theta)
        x_coords = [0, x_final]
        y_coords = [0, y_final]
        return x_coords, y_coords
    
    def obtener_matriz_homogenea(self, theta):
        """
        Retorna la matriz de homogeneidad (transformación) del brazo.
        
        Args:
            theta: Ángulo de la articulación en radianes
            
        Returns:
            Matriz 3x3 de transformación homogénea
        """
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        x = self.L * cos_theta
        y = self.L * sin_theta
        
        # Matriz de transformación homogénea
        T = np.array([
            [cos_theta, -sin_theta, x],
            [sin_theta, cos_theta, y],
            [0, 0, 1]
        ])
        return T


def crear_dashboard():
    """
    Crea un dashboard interactivo para visualizar la cinemática directa.
    """
    # Crear instancia del brazo
    brazo = BrazoRobotico1DOF(longitud_segmento=2.0, angulo_inicial=0)
    
    # Crear figura y subplots
    fig = plt.figure(figsize=(14, 6))
    fig.suptitle('Dashboard - Cinemática Directa (1 DOF)', fontsize=16, fontweight='bold')
    
    # Subplot 1: Visualización del brazo
    ax1 = plt.subplot(1, 2, 1)
    ax1.set_xlim(-2.5, 2.5)
    ax1.set_ylim(-2.5, 2.5)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('X (unidades)', fontsize=10)
    ax1.set_ylabel('Y (unidades)', fontsize=10)
    ax1.set_title('Posición del Brazo Robótico', fontsize=12, fontweight='bold')
    
    # Dibujar el plano de referencia
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=0, color='k', linewidth=0.5)
    
    # Elemento para el brazo
    linea_brazo, = ax1.plot([], [], 'b-', linewidth=3, label='Brazo')
    punto_base, = ax1.plot([0], [0], 'go', markersize=10, label='Base')
    punto_efector, = ax1.plot([], [], 'r*', markersize=20, label='Efector Final')
    
    # Círculo que muestra el rango de movimiento
    circulo = patches.Circle((0, 0), brazo.L, fill=False, 
                             edgecolor='gray', linestyle='--', 
                             linewidth=1, alpha=0.5)
    ax1.add_patch(circulo)
    ax1.legend(loc='upper right', fontsize=10)
    
    # Subplot 2: Información y gráficos
    ax2 = plt.subplot(2, 2, 2)
    ax2.axis('off')
    info_text = ax2.text(0.05, 0.95, '', transform=ax2.transAxes, 
                         fontsize=11, verticalalignment='top',
                         family='monospace', bbox=dict(boxstyle='round', 
                         facecolor='wheat', alpha=0.5))
    
    # Subplot 3: Gráfico de trayectoria
    ax3 = plt.subplot(2, 2, 4)
    ax3.set_xlabel('Ángulo θ (radianes)', fontsize=10)
    ax3.set_ylabel('Posición (unidades)', fontsize=10)
    ax3.set_title('Posición del Efector Final vs Ángulo', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Generar datos para la gráfica
    theta_range = np.linspace(0, 2*np.pi, 100)
    x_range = brazo.L * np.cos(theta_range)
    y_range = brazo.L * np.sin(theta_range)
    
    ax3.plot(theta_range, x_range, 'b-', linewidth=2, label='X (cos)')
    ax3.plot(theta_range, y_range, 'r-', linewidth=2, label='Y (sin)')
    ax3.legend(fontsize=10)
    ax3.set_xlim(0, 2*np.pi)
    
    # Línea vertical para mostrar ángulo actual
    linea_angulo_actual, = ax3.plot([], [], 'g--', linewidth=2, alpha=0.7)
    punto_x_actual, = ax3.plot([], [], 'bo', markersize=8)
    punto_y_actual, = ax3.plot([], [], 'ro', markersize=8)
    
    # Slider para el ángulo
    ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])
    slider_theta = Slider(ax_slider, 'θ (rad)', 0, 2*np.pi, 
                          valinit=0, color='green', alpha=0.7)
    
    def actualizar(val):
        """Actualiza la visualización cuando cambia el ángulo."""
        theta = slider_theta.val
        
        # Actualizar posición del brazo
        x_coords, y_coords = brazo.obtener_segmentos(theta)
        linea_brazo.set_data(x_coords, y_coords)
        
        # Actualizar efector final
        x_final, y_final = brazo.cinematica_directa(theta)
        punto_efector.set_data([x_final], [y_final])
        
        # Actualizar información
        info_str = f"""
PARÁMETROS DEL SISTEMA
─────────────────────────
Ángulo θ:         {np.degrees(theta):7.2f}° ({theta:.4f} rad)
Longitud L:       {brazo.L:.4f} unidades

POSICIÓN DEL EFECTOR FINAL
─────────────────────────
X:                {x_final:7.4f} unidades
Y:                {y_final:7.4f} unidades
Distancia (r):    {np.sqrt(x_final**2 + y_final**2):.4f} unidades
Ángulo (atan2):   {np.degrees(np.arctan2(y_final, x_final)):.2f}°

MATRIZ DE TRANSFORMACIÓN
─────────────────────────
[{np.cos(theta):7.4f}  {-np.sin(theta):7.4f}  {x_final:7.4f}]
[{np.sin(theta):7.4f}  {np.cos(theta):7.4f}  {y_final:7.4f}]
[{0:7.4f}  {0:7.4f}  {1:7.4f}]
"""
        info_text.set_text(info_str)
        
        # Actualizar gráfico de trayectoria
        linea_angulo_actual.set_data([theta, theta], [-brazo.L, brazo.L])
        punto_x_actual.set_data([theta], [x_final])
        punto_y_actual.set_data([theta], [y_final])
        
        fig.canvas.draw_idle()
    
    # Conectar el slider con la función de actualización
    slider_theta.on_changed(actualizar)
    
    # Actualización inicial
    actualizar(0)
    
    # Ajustar espacios manualmente para evitar warnings
    plt.subplots_adjust(left=0.1, right=0.95, top=0.93, bottom=0.15, hspace=0.4, wspace=0.3)
    
    plt.show()


if __name__ == "__main__":
    print("=" * 60)
    print("DASHBOARD DE CINEMÁTICA DIRECTA - 1 DOF")
    print("=" * 60)
    print("\nIniciando dashboard interactivo...")
    print("\nControles:")
    print("  - Mueve el slider para cambiar el ángulo (θ)")
    print("  - Observa la posición del efector final en tiempo real")
    print("  - Los gráficos muestran la relación θ vs posición (x, y)")
    print("\n" + "=" * 60 + "\n")
    
    crear_dashboard()
