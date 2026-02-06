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


class BrazoRobotico2DOF_IK:
    """
    Clase para representar un brazo robótico de 2 DOF con cinemática inversa.
    Permite calcular los ángulos necesarios para alcanzar una posición (x, y).
    """
    
    def __init__(self, L1=1.5, L2=1.0):
        """
        Inicializa el brazo robótico 2DOF.
        
        Args:
            L1: Longitud del primer eslabón
            L2: Longitud del segundo eslabón
        """
        self.L1 = L1
        self.L2 = L2
        
    def cinematica_directa(self, theta1, theta2):
        """
        Calcula la posición del efector final (cinemática directa).
        
        Args:
            theta1: Ángulo de la primera articulación (radianes)
            theta2: Ángulo de la segunda articulación (radianes)
            
        Returns:
            Tupla (x, y) con las coordenadas del efector final
        """
        x = self.L1 * np.cos(theta1) + self.L2 * np.cos(theta1 + theta2)
        y = self.L1 * np.sin(theta1) + self.L2 * np.sin(theta1 + theta2)
        return x, y
    
    def cinematica_inversa(self, x, y, solucion=0):
        """
        Calcula los ángulos necesarios para alcanzar una posición (x, y).
        Cinemática inversa analítica usando geometría.
        
        Args:
            x: Posición X deseada
            y: Posición Y deseada
            solucion: 0 para codo arriba, 1 para codo abajo
            
        Returns:
            Tupla (theta1, theta2) con los ángulos, o (None, None) si no es alcanzable
        """
        # Calcular la distancia desde la base hasta el punto objetivo
        r = np.sqrt(x**2 + y**2)
        
        # Verificar si el punto está dentro del alcance del brazo
        alcance_max = self.L1 + self.L2
        alcance_min = abs(self.L1 - self.L2)
        
        if r > alcance_max or r < alcance_min:
            return None, None
        
        # Aplicar la ley de cosenos para encontrar theta2
        # cos(theta2) = (x^2 + y^2 - L1^2 - L2^2) / (2*L1*L2)
        cos_theta2 = (x**2 + y**2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
        
        # Verificar que el coseno esté en el rango válido
        if abs(cos_theta2) > 1:
            return None, None
        
        # Calcular theta2 (existen dos soluciones)
        if solucion == 0:
            # Codo arriba (theta2 positivo)
            theta2 = np.arccos(cos_theta2)
        else:
            # Codo abajo (theta2 negativo)
            theta2 = -np.arccos(cos_theta2)
        
        # Calcular theta1 usando atan2
        # Ángulo del punto objetivo
        alpha = np.arctan2(y, x)
        
        # Ángulo debido al segundo eslabón
        beta = np.arctan2(self.L2 * np.sin(theta2), 
                          self.L1 + self.L2 * np.cos(theta2))
        
        # theta1 es la diferencia entre estos ángulos
        theta1 = alpha - beta
        
        return theta1, theta2
    
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
        
        # Posición de la segunda articulación
        x_articulo2 = self.L1 * np.cos(theta1)
        y_articulo2 = self.L1 * np.sin(theta1)
        
        # Posición del efector final
        x_efector, y_efector = self.cinematica_directa(theta1, theta2)
        
        # Coordenadas para dibujar los eslabones
        x_coords = [x_articulo1, x_articulo2, x_efector]
        y_coords = [y_articulo1, y_articulo2, y_efector]
        
        return x_coords, y_coords, (x_articulo2, y_articulo2)
    
    def obtener_espacio_trabajo(self, num_puntos=100):
        """
        Genera el espacio de trabajo del brazo (todos los puntos alcanzables).
        
        Args:
            num_puntos: Número de puntos para generar el espacio
            
        Returns:
            Tupla (x_puntos, y_puntos) con las coordenadas del espacio de trabajo
        """
        x_trabajo = []
        y_trabajo = []
        
        theta1_range = np.linspace(0, 2*np.pi, num_puntos)
        theta2_range = np.linspace(-np.pi, np.pi, num_puntos)
        
        for t1 in theta1_range:
            for t2 in theta2_range:
                x, y = self.cinematica_directa(t1, t2)
                x_trabajo.append(x)
                y_trabajo.append(y)
        
        return np.array(x_trabajo), np.array(y_trabajo)


def crear_dashboard_ik_2dof():
    """
    Crea un dashboard interactivo para visualizar la cinemática inversa de 2DOF.
    """
    # Crear instancia del brazo
    brazo = BrazoRobotico2DOF_IK(L1=1.5, L2=1.0)
    
    # Generar espacio de trabajo
    print("Generando espacio de trabajo... (esto puede tomar unos segundos)")
    x_trabajo, y_trabajo = brazo.obtener_espacio_trabajo(num_puntos=80)
    print("Espacio de trabajo generado.")
    
    # Crear figura y subplots
    fig = plt.figure(figsize=(16, 7))
    fig.suptitle('Dashboard - Cinemática Inversa (2 DOF)', fontsize=16, fontweight='bold')
    
    # Subplot 1: Visualización del brazo y espacio de trabajo
    ax1 = plt.subplot(1, 2, 1)
    alcance_max = brazo.L1 + brazo.L2
    ax1.set_xlim(-alcance_max - 0.5, alcance_max + 0.5)
    ax1.set_ylim(-alcance_max - 0.5, alcance_max + 0.5)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('X (unidades)', fontsize=10)
    ax1.set_ylabel('Y (unidades)', fontsize=10)
    ax1.set_title('Espacio de Trabajo y Posición del Brazo', fontsize=12, fontweight='bold')
    
    # Dibujar el plano de referencia
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=0, color='k', linewidth=0.5)
    
    # Dibujar espacio de trabajo
    ax1.scatter(x_trabajo, y_trabajo, c='lightgray', s=1, alpha=0.3, label='Espacio de trabajo')
    
    # Elementos para los eslabones
    linea_eslabon1, = ax1.plot([], [], 'b-', linewidth=4, label='Eslabón 1', alpha=0.7)
    linea_eslabon2, = ax1.plot([], [], 'c-', linewidth=3, label='Eslabón 2', alpha=0.7)
    punto_base, = ax1.plot([0], [0], 'go', markersize=12, label='Base', zorder=5)
    punto_articulo2, = ax1.plot([], [], 'yo', markersize=10, label='Articulación 2', zorder=5)
    punto_efector, = ax1.plot([], [], 'r*', markersize=25, label='Efector Final', zorder=5)
    punto_objetivo, = ax1.plot([], [], 'mx', markersize=15, markeredgewidth=2, 
                               label='Objetivo', zorder=5)
    
    # Círculos de alcance
    circulo_interno = patches.Circle((0, 0), brazo.L1 - brazo.L2, fill=False, 
                                     edgecolor='gray', linestyle=':', 
                                     linewidth=1, alpha=0.3)
    circulo_externo = patches.Circle((0, 0), alcance_max, fill=False, 
                                     edgecolor='gray', linestyle='--', 
                                     linewidth=1, alpha=0.5)
    ax1.add_patch(circulo_interno)
    ax1.add_patch(circulo_externo)
    ax1.legend(loc='upper right', fontsize=8)
    
    # Subplot 2: Información del sistema
    ax2 = plt.subplot(2, 2, 2)
    ax2.axis('off')
    info_text = ax2.text(0.05, 0.95, '', transform=ax2.transAxes, 
                         fontsize=9, verticalalignment='top',
                         family='monospace', bbox=dict(boxstyle='round', 
                         facecolor='lightblue', alpha=0.5))
    
    # Subplot 3: Control de posición
    ax3 = plt.subplot(2, 2, 4)
    ax3.axis('off')
    
    # Sliders para la posición objetivo
    ax_slider_x = plt.axes([0.55, 0.25, 0.35, 0.02])
    ax_slider_y = plt.axes([0.55, 0.20, 0.35, 0.02])
    ax_radio_sol = plt.axes([0.55, 0.13, 0.35, 0.05])
    
    slider_x = Slider(ax_slider_x, 'X objetivo', -alcance_max, alcance_max, 
                      valinit=1.5, color='red', alpha=0.7)
    slider_y = Slider(ax_slider_y, 'Y objetivo', -alcance_max, alcance_max, 
                      valinit=1.5, color='red', alpha=0.7)
    
    # Radio buttons para seleccionar solución
    from matplotlib.widgets import RadioButtons
    ax_radio_sol.text(0.1, 0.9, 'Solución IK:', transform=ax_radio_sol.transAxes,
                      fontsize=11, fontweight='bold', verticalalignment='top')
    radio_solucion = RadioButtons(ax_radio_sol, ('Codo Arriba', 'Codo Abajo'), 
                                  active=0)
    
    def actualizar(val):
        """Actualiza la visualización cuando cambian los parámetros."""
        x_objetivo = slider_x.val
        y_objetivo = slider_y.val
        solucion = radio_solucion.value_selected
        
        # Convertir selección a índice
        idx_solucion = 0 if solucion == 'Codo Arriba' else 1
        
        # Calcular cinemática inversa
        theta1, theta2 = brazo.cinematica_inversa(x_objetivo, y_objetivo, solucion=idx_solucion)
        
        # Actualizar punto objetivo
        punto_objetivo.set_data([x_objetivo], [y_objetivo])
        
        if theta1 is None:
            # Posición no alcanzable
            info_str = f"""
PARÁMETROS DEL SISTEMA
──────────────────────────────
L1:               {brazo.L1:.4f} unidades
L2:               {brazo.L2:.4f} unidades

OBJETIVO
──────────────────────────────
X deseado:        {x_objetivo:7.4f} unidades
Y deseado:        {y_objetivo:7.4f} unidades

RESULTADO
──────────────────────────────
⚠ POSICIÓN NO ALCANZABLE
Está fuera del espacio de trabajo.

Alcance máximo:   {brazo.L1 + brazo.L2:.4f} unidades
Alcance mínimo:   {abs(brazo.L1 - brazo.L2):.4f} unidades
Distancia actual: {np.sqrt(x_objetivo**2 + y_objetivo**2):.4f} unidades
"""
            # Limpiar eslabones
            linea_eslabon1.set_data([], [])
            linea_eslabon2.set_data([], [])
            punto_articulo2.set_data([], [])
            punto_efector.set_data([], [])
        else:
            # Posición alcanzable
            x_coords, y_coords, pos_art2 = brazo.obtener_articulos(theta1, theta2)
            
            # Actualizar eslabones
            linea_eslabon1.set_data([x_coords[0], x_coords[1]], 
                                    [y_coords[0], y_coords[1]])
            linea_eslabon2.set_data([x_coords[1], x_coords[2]], 
                                    [y_coords[1], y_coords[2]])
            
            # Actualizar puntos
            punto_articulo2.set_data([pos_art2[0]], [pos_art2[1]])
            punto_efector.set_data([x_coords[2]], [y_coords[2]])
            
            # Calcular error de posicionamiento
            error_x = x_coords[2] - x_objetivo
            error_y = y_coords[2] - y_objetivo
            error_total = np.sqrt(error_x**2 + error_y**2)
            
            # Información detallada
            info_str = f"""
PARÁMETROS DEL SISTEMA
──────────────────────────────
L1:               {brazo.L1:.4f} unidades
L2:               {brazo.L2:.4f} unidades

OBJETIVO
──────────────────────────────
X deseado:        {x_objetivo:7.4f} unidades
Y deseado:        {y_objetivo:7.4f} unidades

SOLUCIÓN - ÁNGULOS CALCULADOS
──────────────────────────────
θ1:               {np.degrees(theta1):7.2f}° ({theta1:.4f} rad)
θ2:               {np.degrees(theta2):7.2f}° ({theta2:.4f} rad)
θ_total:          {np.degrees(theta1+theta2):7.2f}°
Tipo solución:    {solucion}

EFECTOR FINAL REAL
──────────────────────────────
X alcanzado:      {x_coords[2]:7.4f} unidades
Y alcanzado:      {y_coords[2]:7.4f} unidades

ERROR DE POSICIÓN
──────────────────────────────
ΔX:               {error_x:7.6f} unidades
ΔY:               {error_y:7.6f} unidades
Error total:      {error_total:7.6f} unidades
"""
        
        info_text.set_text(info_str)
        fig.canvas.draw_idle()
    
    # Conectar los controles con la función de actualización
    slider_x.on_changed(actualizar)
    slider_y.on_changed(actualizar)
    radio_solucion.on_clicked(lambda label: actualizar(None))
    
    # Actualización inicial
    actualizar(None)
    
    plt.subplots_adjust(left=0.08, right=0.95, top=0.93, bottom=0.15, hspace=0.4, wspace=0.25)
    plt.show()


if __name__ == "__main__":
    print("=" * 80)
    print("DASHBOARD DE CINEMÁTICA INVERSA - 2 DOF (BRAZO DE 2 ESLABONES)")
    print("=" * 80)
    print("\nIniciando dashboard interactivo...")
    print("\nCaracterísticas:")
    print("  - Brazo con 2 eslabones en el plano XY")
    print("  - Soluciona el problema de cinemática inversa analíticamente")
    print("  - Muestra el espacio de trabajo (área alcanzable)")
    print("\nFórmulas utilizadas:")
    print("  - Ley de cosenos para calcular θ2")
    print("  - atan2 para calcular θ1")
    print("  - Dos soluciones posibles: codo arriba (elbow-up) y codo abajo (elbow-down)")
    print("\nControles:")
    print("  - Slider X: Posición X objetivo (-3.5 a 3.5)")
    print("  - Slider Y: Posición Y objetivo (-3.5 a 3.5)")
    print("  - Radio buttons: Seleccionar tipo de solución (codo arriba/abajo)")
    print("\nVisualización:")
    print("  - Puntos grises: Espacio de trabajo (área alcanzable)")
    print("  - Círculos: Rango de alcance mínimo y máximo")
    print("  - X magenta: Punto objetivo deseado")
    print("  - Eslabones: Configuración calculada del brazo")
    print("\n" + "=" * 80 + "\n")
    
    crear_dashboard_ik_2dof()
