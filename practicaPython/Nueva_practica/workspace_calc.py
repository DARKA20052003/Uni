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
from scipy.spatial import ConvexHull


class CalculadoraWorkspace2DOF:
    """
    Clase para calcular y analizar el workspace de un brazo robótico 2DOF.
    """
    
    def __init__(self, L1=1.5, L2=1.0, num_puntos=150):
        """
        Inicializa la calculadora de workspace.
        
        Args:
            L1: Longitud del primer eslabón
            L2: Longitud del segundo eslabón
            num_puntos: Número de puntos por dimensión para generar el workspace
        """
        self.L1 = L1
        self.L2 = L2
        self.num_puntos = num_puntos
        self.workspace_x = None
        self.workspace_y = None
        self.workspace_calculado = False
        
    def cinematica_directa(self, theta1, theta2):
        """
        Calcula la posición del efector final.
        
        Args:
            theta1: Ángulo de la primera articulación (radianes)
            theta2: Ángulo de la segunda articulación (radianes)
            
        Returns:
            Tupla (x, y) con las coordenadas del efector final
        """
        x = self.L1 * np.cos(theta1) + self.L2 * np.cos(theta1 + theta2)
        y = self.L1 * np.sin(theta1) + self.L2 * np.sin(theta1 + theta2)
        return x, y
    
    def calcular_workspace(self):
        """
        Calcula todos los puntos alcanzables del workspace.
        
        Returns:
            Tupla (x_puntos, y_puntos) con las coordenadas del workspace
        """
        x_puntos = []
        y_puntos = []
        
        # Generar rango de ángulos
        theta1_range = np.linspace(0, 2*np.pi, self.num_puntos)
        theta2_range = np.linspace(-np.pi, np.pi, self.num_puntos)
        
        # Calcular cinemática directa para cada combinación
        for t1 in theta1_range:
            for t2 in theta2_range:
                x, y = self.cinematica_directa(t1, t2)
                x_puntos.append(x)
                y_puntos.append(y)
        
        self.workspace_x = np.array(x_puntos)
        self.workspace_y = np.array(y_puntos)
        self.workspace_calculado = True
        
        return self.workspace_x, self.workspace_y
    
    def obtener_estadisticas_workspace(self):
        """
        Calcula estadísticas del workspace.
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.workspace_calculado:
            self.calcular_workspace()
        
        # Distancia radial desde origen
        r = np.sqrt(self.workspace_x**2 + self.workspace_y**2)
        
        stats = {
            'x_max': np.max(self.workspace_x),
            'x_min': np.min(self.workspace_x),
            'y_max': np.max(self.workspace_y),
            'y_min': np.min(self.workspace_y),
            'r_max': np.max(r),
            'r_min': np.min(r),
            'area_aprox': self._calcular_area_convexa(),
            'alcance_maximo': self.L1 + self.L2,
            'alcance_minimo': abs(self.L1 - self.L2),
            'num_puntos': len(self.workspace_x)
        }
        
        return stats
    
    def _calcular_area_convexa(self):
        """
        Calcula el área aproximada del workspace usando el casco convexo.
        
        Returns:
            Área del casco convexo
        """
        try:
            puntos = np.column_stack((self.workspace_x, self.workspace_y))
            casco = ConvexHull(puntos)
            return casco.volume  # En 2D, volume da el área
        except:
            return None
    
    def obtener_casco_convexo(self):
        """
        Retorna los puntos del casco convexo del workspace.
        
        Returns:
            Tupla (x_casco, y_casco)
        """
        try:
            puntos = np.column_stack((self.workspace_x, self.workspace_y))
            casco = ConvexHull(puntos)
            vertices = casco.vertices
            x_casco = self.workspace_x[vertices]
            y_casco = self.workspace_y[vertices]
            return x_casco, y_casco
        except:
            return None, None
    
    def obtener_circulos_alcance(self):
        """
        Retorna los parámetros de los círculos que delimitan el workspace.
        
        Returns:
            Tupla (radio_externo, radio_interno)
        """
        return self.L1 + self.L2, abs(self.L1 - self.L2)


def crear_dashboard_workspace():
    """
    Crea un dashboard interactivo para visualizar el workspace de 2DOF.
    """
    # Crear instancia de la calculadora
    calc = CalculadoraWorkspace2DOF(L1=1.5, L2=1.0, num_puntos=120)
    
    # Calcular workspace inicial
    print("Calculando workspace inicial...")
    x_work, y_work = calc.calcular_workspace()
    print("Workspace calculado. Iniciando dashboard...")
    
    # Crear figura
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Dashboard - Análisis de Workspace (2 DOF)', fontsize=16, fontweight='bold')
    
    # Subplot 1: Visualización principal del workspace
    ax1 = plt.subplot(2, 2, 1)
    alcance_max_inicial = calc.L1 + calc.L2
    ax1.set_xlim(-alcance_max_inicial - 1, alcance_max_inicial + 1)
    ax1.set_ylim(-alcance_max_inicial - 1, alcance_max_inicial + 1)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('X (unidades)', fontsize=10)
    ax1.set_ylabel('Y (unidades)', fontsize=10)
    ax1.set_title('Espacio de Trabajo del Brazo', fontsize=12, fontweight='bold')
    
    # Dibujar ejes de referencia
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=0, color='k', linewidth=0.5)
    
    # Scatter plot del workspace
    scatter_work = ax1.scatter(x_work, y_work, c='lightblue', s=2, alpha=0.4, 
                               label='Workspace')
    
    # Elementos para visualización
    casco_x, casco_y = calc.obtener_casco_convexo()
    if casco_x is not None:
        # Cerrar el polígono para que cierre correctamente
        casco_x_cerrado = np.append(casco_x, casco_x[0])
        casco_y_cerrado = np.append(casco_y, casco_y[0])
        linea_casco, = ax1.plot(casco_x_cerrado, casco_y_cerrado, 'r-', 
                                linewidth=2, label='Casco Convexo')
    
    circulo_externo = patches.Circle((0, 0), calc.L1 + calc.L2, fill=False, 
                                     edgecolor='green', linestyle='--', 
                                     linewidth=1.5, alpha=0.6, label='Alcance máximo')
    circulo_interno = patches.Circle((0, 0), abs(calc.L1 - calc.L2), fill=False, 
                                     edgecolor='orange', linestyle=':', 
                                     linewidth=1.5, alpha=0.6, label='Alcance mínimo')
    ax1.add_patch(circulo_externo)
    ax1.add_patch(circulo_interno)
    
    punto_base, = ax1.plot([0], [0], 'ko', markersize=10, label='Base', zorder=5)
    ax1.legend(loc='upper right', fontsize=9)
    
    # Subplot 2: Información y estadísticas
    ax2 = plt.subplot(2, 2, 2)
    ax2.axis('off')
    info_text = ax2.text(0.05, 0.95, '', transform=ax2.transAxes, 
                         fontsize=10, verticalalignment='top',
                         family='monospace', bbox=dict(boxstyle='round', 
                         facecolor='lightyellow', alpha=0.7))
    
    # Subplot 3: Distribución radial
    ax3 = plt.subplot(2, 2, 3)
    ax3.set_xlabel('Radio r (unidades)', fontsize=10)
    ax3.set_ylabel('Frecuencia', fontsize=10)
    ax3.set_title('Distribución de Distancias Radiales', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    hist_plot = None
    
    # Subplot 4: Cobertura angular
    ax4 = plt.subplot(2, 2, 4)
    ax4.set_xlabel('Ángulo (grados)', fontsize=10)
    ax4.set_ylabel('Radio alcanzado (unidades)', fontsize=10)
    ax4.set_title('Alcance vs Ángulo', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Sliders para L1 y L2
    ax_slider_L1 = plt.axes([0.2, 0.08, 0.25, 0.02])
    ax_slider_L2 = plt.axes([0.2, 0.04, 0.25, 0.02])
    
    slider_L1 = Slider(ax_slider_L1, 'L1', 0.5, 3.0, valinit=1.5, 
                       color='blue', alpha=0.7)
    slider_L2 = Slider(ax_slider_L2, 'L2', 0.5, 3.0, valinit=1.0, 
                       color='cyan', alpha=0.7)
    
    def actualizar(val):
        """Actualiza el dashboard cuando cambian L1 o L2."""
        L1 = slider_L1.val
        L2 = slider_L2.val
        
        # Actualizar calculadora
        calc.L1 = L1
        calc.L2 = L2
        calc.workspace_calculado = False
        
        print(f"Calculando workspace para L1={L1:.2f}, L2={L2:.2f}...")
        x_work, y_work = calc.calcular_workspace()
        
        # Actualizar scatter plot
        scatter_work.set_offsets(np.c_[x_work, y_work])
        
        # Actualizar casco convexo
        casco_x, casco_y = calc.obtener_casco_convexo()
        if casco_x is not None:
            casco_x_cerrado = np.append(casco_x, casco_x[0])
            casco_y_cerrado = np.append(casco_y, casco_y[0])
            linea_casco.set_data(casco_x_cerrado, casco_y_cerrado)
        
        # Actualizar círculos
        alcance_max = L1 + L2
        alcance_min = abs(L1 - L2)
        circulo_externo.set_radius(alcance_max)
        circulo_interno.set_radius(alcance_min)
        
        # Actualizar límites de los ejes
        ax1.set_xlim(-alcance_max - 0.5, alcance_max + 0.5)
        ax1.set_ylim(-alcance_max - 0.5, alcance_max + 0.5)
        
        # Obtener estadísticas
        stats = calc.obtener_estadisticas_workspace()
        
        # Actualizar información
        info_str = f"""
PARÁMETROS DEL SISTEMA
────────────────────────────
L1:               {L1:.4f} unidades
L2:               {L2:.4f} unidades

CARACTERÍSTICAS DEL WORKSPACE
────────────────────────────
Alcance máximo:   {stats['alcance_maximo']:.4f} unidades
Alcance mínimo:   {stats['alcance_minimo']:.4f} unidades
Área aprox.:      {stats['area_aprox']:.4f} unidades²

EXTENSIÓN DEL WORKSPACE
────────────────────────────
X_máx:            {stats['x_max']:7.4f} unidades
X_mín:            {stats['x_min']:7.4f} unidades
Y_máx:            {stats['y_max']:7.4f} unidades
Y_mín:            {stats['y_min']:7.4f} unidades
R_máx:            {stats['r_max']:7.4f} unidades
R_mín:            {stats['r_min']:7.4f} unidades

ANÁLISIS
────────────────────────────
Puntos muestreados: {stats['num_puntos']:,}
Relación L1/L2:   {L1/L2 if L2 > 0 else 0:.4f}
"""
        info_text.set_text(info_str)
        
        # Actualizar histograma de distancias radiales
        r = np.sqrt(x_work**2 + y_work**2)
        ax3.clear()
        ax3.hist(r, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        ax3.set_xlabel('Radio r (unidades)', fontsize=10)
        ax3.set_ylabel('Frecuencia', fontsize=10)
        ax3.set_title('Distribución de Distancias Radiales', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.axvline(x=stats['r_max'], color='green', linestyle='--', 
                   linewidth=2, label=f"R_máx: {stats['r_max']:.2f}")
        ax3.axvline(x=stats['r_min'], color='orange', linestyle=':', 
                   linewidth=2, label=f"R_mín: {stats['r_min']:.2f}")
        ax3.legend(fontsize=9)
        
        # Actualizar gráfico de alcance vs ángulo
        ax4.clear()
        theta_range = np.linspace(0, 2*np.pi, 100)
        r_max_angle = []
        r_min_angle = []
        
        for theta in theta_range:
            # Encontrar máximo y mínimo radio para cada ángulo
            mask_theta = np.abs(np.arctan2(y_work, x_work) - theta) < 0.1
            if np.any(mask_theta):
                r_angle = np.sqrt(x_work[mask_theta]**2 + y_work[mask_theta]**2)
                r_max_angle.append(np.max(r_angle))
                r_min_angle.append(np.min(r_angle))
            else:
                r_max_angle.append(np.nan)
                r_min_angle.append(np.nan)
        
        theta_degrees = np.degrees(theta_range)
        ax4.plot(theta_degrees, r_max_angle, 'g-', linewidth=2, label='R máximo')
        ax4.plot(theta_degrees, r_min_angle, 'orange', linewidth=2, label='R mínimo')
        ax4.fill_between(theta_degrees, r_min_angle, r_max_angle, alpha=0.2, color='blue')
        ax4.set_xlabel('Ángulo (grados)', fontsize=10)
        ax4.set_ylabel('Radio alcanzado (unidades)', fontsize=10)
        ax4.set_title('Alcance vs Ángulo', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim(0, 360)
        ax4.legend(fontsize=9)
        
        fig.canvas.draw_idle()
        print("Dashboard actualizado.")
    
    # Conectar sliders
    slider_L1.on_changed(actualizar)
    slider_L2.on_changed(actualizar)
    
    # Actualización inicial
    actualizar(None)
    
    plt.subplots_adjust(left=0.1, right=0.95, top=0.93, bottom=0.15, hspace=0.35, wspace=0.3)
    plt.show()


if __name__ == "__main__":
    print("=" * 80)
    print("DASHBOARD DE ANÁLISIS DE WORKSPACE - 2 DOF")
    print("=" * 80)
    print("\nCaracterísticas:")
    print("  - Visualización completa del espacio de trabajo alcanzable")
    print("  - Cálculo del casco convexo (límite exterior)")
    print("  - Análisis de distribución de alcance radial")
    print("  - Cobertura angular del workspace")
    print("  - Parámetros ajustables en tiempo real")
    print("\nControles:")
    print("  - Slider L1: Ajusta la longitud del primer eslabón (0.5 a 3.0)")
    print("  - Slider L2: Ajusta la longitud del segundo eslabón (0.5 a 3.0)")
    print("\nVisualizaciones:")
    print("  - Panel superior izquierdo: Workspace completo con casco convexo")
    print("  - Panel superior derecho: Estadísticas del sistema")
    print("  - Panel inferior izquierdo: Histograma de distancias radiales")
    print("  - Panel inferior derecho: Alcance vs ángulo de cobertura")
    print("\n" + "=" * 80 + "\n")
    
    crear_dashboard_workspace()
