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


class CalculadoraWorkspace3DOF:
    """
    Clase para calcular y analizar el workspace de un brazo robótico 3DOF antropomórfico.
    Simula un brazo tipo robot humanoide con hombro, codo y muñeca.
    
    Proporciones antropomórficas:
    - L1 (Antebrazo): ~40% de la longitud total
    - L2 (Brazo): ~35% de la longitud total
    - L3 (Muñeca): ~25% de la longitud total
    """
    
    def __init__(self, L1=1.4, L2=1.2, L3=0.9, num_puntos=80):
        """
        Inicializa la calculadora de workspace 3DOF antropomórfico.
        
        Args:
            L1: Longitud del primer eslabón (hombro-codo) - típicamente más largo
            L2: Longitud del segundo eslabón (codo-muñeca) - típicamente intermedio
            L3: Longitud del tercer eslabón (muñeca-efector) - típicamente más corto
            num_puntos: Número de puntos por dimensión para generar el workspace
        """
        self.L1 = L1  # Eslabón superior (hombro-codo)
        self.L2 = L2  # Eslabón intermedio (codo-muñeca)
        self.L3 = L3  # Eslabón inferior (muñeca-mano)
        self.num_puntos = num_puntos
        self.workspace_x = None
        self.workspace_y = None
        self.workspace_calculado = False
        
        # Nombres de las articulaciones
        self.nombre_articulos = ['Base (Hombro)', 'Codo', 'Muñeca', 'Efector Final']
        
    def cinematica_directa(self, theta1, theta2, theta3):
        """
        Calcula la posición del efector final para 3DOF.
        
        Fórmulas:
        x = L1*cos(θ1) + L2*cos(θ1+θ2) + L3*cos(θ1+θ2+θ3)
        y = L1*sin(θ1) + L2*sin(θ1+θ2) + L3*sin(θ1+θ2+θ3)
        
        Args:
            theta1: Ángulo de la primera articulación (radianes)
            theta2: Ángulo de la segunda articulación (radianes)
            theta3: Ángulo de la tercera articulación (radianes)
            
        Returns:
            Tupla (x, y) con las coordenadas del efector final
        """
        # Ángulos acumulados
        a1 = theta1
        a2 = theta1 + theta2
        a3 = theta1 + theta2 + theta3
        
        x = self.L1 * np.cos(a1) + self.L2 * np.cos(a2) + self.L3 * np.cos(a3)
        y = self.L1 * np.sin(a1) + self.L2 * np.sin(a2) + self.L3 * np.sin(a3)
        
        return x, y
    
    def obtener_articulos(self, theta1, theta2, theta3):
        """
        Retorna las posiciones de todas las articulaciones.
        
        Args:
            theta1, theta2, theta3: Ángulos de las articulaciones
            
        Returns:
            Tupla (x_coords, y_coords) con las coordenadas de todos los puntos
        """
        # Posición base
        x0, y0 = 0, 0
        
        # Primera articulación
        x1 = self.L1 * np.cos(theta1)
        y1 = self.L1 * np.sin(theta1)
        
        # Segunda articulación
        a2 = theta1 + theta2
        x2 = x1 + self.L2 * np.cos(a2)
        y2 = y1 + self.L2 * np.sin(a2)
        
        # Efector final (tercera articulación)
        a3 = theta1 + theta2 + theta3
        x3 = x2 + self.L3 * np.cos(a3)
        y3 = y2 + self.L3 * np.sin(a3)
        
        x_coords = [x0, x1, x2, x3]
        y_coords = [y0, y1, y2, y3]
        
        return x_coords, y_coords
    
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
        theta3_range = np.linspace(-np.pi, np.pi, self.num_puntos)
        
        # Calcular cinemática directa para cada combinación
        # Nota: Para 3DOF usamos muestreo reducido para velocidad
        for t1 in theta1_range:
            for t2 in theta2_range[::3]:  # Reducir muestreo
                for t3 in theta3_range[::3]:
                    x, y = self.cinematica_directa(t1, t2, t3)
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
            'alcance_maximo': self.L1 + self.L2 + self.L3,
            'alcance_minimo': abs(self.L1 - self.L2 - self.L3),
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


def crear_dashboard_workspace_3dof():
    """
    Crea un dashboard interactivo para visualizar el workspace de brazo antropomórfico 3DOF.
    """
    # Crear instancia de la calculadora con proporciones antropomórficas
    calc = CalculadoraWorkspace3DOF(L1=1.4, L2=1.2, L3=0.9, num_puntos=60)
    
    # Calcular workspace inicial
    print("Calculando workspace inicial para brazo antropomórfico 3DOF...")
    x_work, y_work = calc.calcular_workspace()
    print(f"Workspace calculado con {len(x_work)} puntos.")
    
    # Crear figura
    fig = plt.figure(figsize=(18, 10))
    fig.patch.set_facecolor('#f5f5f5')
    fig.suptitle('Dashboard - Análisis de Workspace - Brazo Antropomórfico 3DOF', 
                 fontsize=16, fontweight='bold', color='#333333')
    
    # Subplot 1: Visualización principal del workspace
    ax1 = plt.subplot(2, 2, 1)
    ax1.set_facecolor('#ffffff')
    alcance_max_inicial = calc.L1 + calc.L2 + calc.L3
    ax1.set_xlim(-alcance_max_inicial - 0.8, alcance_max_inicial + 0.8)
    ax1.set_ylim(-0.5, alcance_max_inicial + 0.8)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.2, color='gray', linestyle=':')
    ax1.set_xlabel('X (unidades)', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Y (unidades)', fontsize=10, fontweight='bold')
    ax1.set_title('Espacio de Trabajo - Brazo Antropomórfico', fontsize=12, fontweight='bold')
    
    # Dibujar ejes de referencia
    ax1.axhline(y=0, color='black', linewidth=1, alpha=0.5)
    ax1.axvline(x=0, color='black', linewidth=1, alpha=0.5)
    
    # Scatter plot del workspace con degradado
    scatter_work = ax1.scatter(x_work, y_work, c='#87CEEB', s=3, alpha=0.6, 
                               label='Workspace alcanzable', edgecolors='none')
    
    # Casco convexo con relleno
    casco_x, casco_y = calc.obtener_casco_convexo()
    if casco_x is not None:
        casco_x_cerrado = np.append(casco_x, casco_x[0])
        casco_y_cerrado = np.append(casco_y, casco_y[0])
        ax1.fill(casco_x_cerrado, casco_y_cerrado, color='#FFB6C1', alpha=0.2, 
                label='Límite exterior (casco convexo)')
        linea_casco, = ax1.plot(casco_x_cerrado, casco_y_cerrado, 'r-', 
                                linewidth=2.5, label='Casco Convexo', zorder=4)
    
    # Círculo de alcance máximo
    circulo_externo = patches.Circle((0, 0), calc.L1 + calc.L2 + calc.L3, fill=False, 
                                     edgecolor='#FF8C00', linestyle='--', 
                                     linewidth=2, alpha=0.7, label='Círculo de alcance máximo')
    ax1.add_patch(circulo_externo)
    
    # Base del brazo (hombro)
    punto_base, = ax1.plot([0], [0], 'o', color='#2F4F4F', markersize=15, 
                           label='Hombro (Base)', zorder=5)
    
    # Línea del suelo
    ax1.plot([-alcance_max_inicial-0.5, alcance_max_inicial+0.5], [0, 0], 
            'k-', linewidth=2, alpha=0.3)
    
    ax1.legend(loc='upper left', fontsize=9, framealpha=0.95)
    
    # Subplot 2: Información y estadísticas
    ax2 = plt.subplot(2, 2, 2)
    ax2.axis('off')
    ax2.set_facecolor('#f0f8ff')
    info_text = ax2.text(0.05, 0.95, '', transform=ax2.transAxes, 
                         fontsize=9.5, verticalalignment='top',
                         family='monospace', bbox=dict(boxstyle='round', 
                         facecolor='#E6F2FF', alpha=0.9, edgecolor='#4169E1', linewidth=2))
    
    # Subplot 3: Distribución radial
    ax3 = plt.subplot(2, 2, 3)
    ax3.set_facecolor('#ffffff')
    ax3.set_xlabel('Radio r (unidades)', fontsize=10, fontweight='bold')
    ax3.set_ylabel('Frecuencia', fontsize=10, fontweight='bold')
    ax3.set_title('Distribución de Distancias Radiales', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.2, color='gray', linestyle=':')
    
    # Subplot 4: Cobertura angular
    ax4 = plt.subplot(2, 2, 4)
    ax4.set_facecolor('#ffffff')
    ax4.set_xlabel('Ángulo de Posición (grados)', fontsize=10, fontweight='bold')
    ax4.set_ylabel('Radio (unidades)', fontsize=10, fontweight='bold')
    ax4.set_title('Cobertura Radial por Ángulo', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.2, color='gray', linestyle=':')
    
    # Sliders para L1, L2 y L3 con etiquetas antropomórficas
    ax_slider_L1 = plt.axes([0.15, 0.13, 0.25, 0.02])
    ax_slider_L2 = plt.axes([0.15, 0.09, 0.25, 0.02])
    ax_slider_L3 = plt.axes([0.15, 0.05, 0.25, 0.02])
    
    slider_L1 = Slider(ax_slider_L1, 'L1 (Brazo)', 0.8, 2.5, valinit=1.4, 
                       color='#4169E1', alpha=0.8)
    slider_L2 = Slider(ax_slider_L2, 'L2 (Antebrazo)', 0.6, 2.5, valinit=1.2, 
                       color='#20B2AA', alpha=0.8)
    slider_L3 = Slider(ax_slider_L3, 'L3 (Mano)', 0.3, 1.5, valinit=0.9, 
                       color='#FF69B4', alpha=0.8)
    
    def actualizar(val):
        """Actualiza el dashboard cuando cambian L1, L2 o L3."""
        L1 = slider_L1.val
        L2 = slider_L2.val
        L3 = slider_L3.val
        
        # Actualizar calculadora
        calc.L1 = L1
        calc.L2 = L2
        calc.L3 = L3
        calc.workspace_calculado = False
        
        print(f"Calculando workspace para L1={L1:.2f}, L2={L2:.2f}, L3={L3:.2f}...")
        x_work, y_work = calc.calcular_workspace()
        
        # Actualizar scatter plot
        scatter_work.set_offsets(np.c_[x_work, y_work])
        
        # Actualizar casco convexo
        casco_x, casco_y = calc.obtener_casco_convexo()
        if casco_x is not None:
            casco_x_cerrado = np.append(casco_x, casco_x[0])
            casco_y_cerrado = np.append(casco_y, casco_y[0])
            linea_casco.set_data(casco_x_cerrado, casco_y_cerrado)
        
        # Actualizar círculo de alcance máximo
        alcance_max = L1 + L2 + L3
        circulo_externo.set_radius(alcance_max)
        
        # Actualizar límites de los ejes
        ax1.set_xlim(-alcance_max - 0.8, alcance_max + 0.8)
        ax1.set_ylim(-0.5, alcance_max + 0.8)
        
        # Obtener estadísticas
        stats = calc.obtener_estadisticas_workspace()
        
        # Actualizar información con etiquetas antropomórficas
        info_str = f"""
╔══════════════════════════════════╗
║     BRAZO ANTROPOMÓRFICO 3DOF    ║
╚══════════════════════════════════╝

DIMENSIONES DEL BRAZO
─────────────────────────────────
L1 (Brazo):       {L1:.4f} unidades
L2 (Antebrazo):   {L2:.4f} unidades
L3 (Mano):        {L3:.4f} unidades
Total:            {L1+L2+L3:.4f} unidades

CARACTERÍSTICAS DEL WORKSPACE
─────────────────────────────────
Alcance máximo:   {stats['alcance_maximo']:.4f} unidades
Alcance mínimo:   {stats['alcance_minimo']:.4f} unidades
Área aprox.:      {stats['area_aprox']:.4f} unidades²

EXTENSIÓN DEL WORKSPACE
─────────────────────────────────
Horizontal (ΔX):  {stats['x_max']-stats['x_min']:7.4f} un
Vertical (ΔY):    {stats['y_max']-stats['y_min']:7.4f} un
Radio máximo:     {stats['r_max']:7.4f} unidades

PROPORCIONES
─────────────────────────────────
L1:L2:L3 =        {L1/L1:.2f}:{L2/L1:.2f}:{L3/L1:.2f}
Puntos calc.:     {stats['num_puntos']:,}
"""
        info_text.set_text(info_str)
        
        # Actualizar histograma de distancias radiales
        r = np.sqrt(x_work**2 + y_work**2)
        ax3.clear()
        ax3.hist(r, bins=60, color='#87CEEB', edgecolor='#4169E1', alpha=0.8)
        ax3.axvline(x=stats['r_max'], color='#FF6347', linestyle='--', 
                   linewidth=2.5, label=f"Máx: {stats['r_max']:.2f}")
        ax3.axvline(x=stats['r_min'], color='#FFB6C1', linestyle=':', 
                   linewidth=2.5, label=f"Mín: {stats['r_min']:.2f}")
        ax3.set_xlabel('Radio r (unidades)', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Frecuencia', fontsize=10, fontweight='bold')
        ax3.set_title('Distribución de Distancias Radiales', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.2, color='gray', linestyle=':')
        ax3.set_facecolor('#ffffff')
        ax3.legend(fontsize=9, framealpha=0.95)
        
        # Actualizar gráfico de cobertura angular
        ax4.clear()
        theta_angles = np.linspace(0, 360, 120)
        r_max_angle = []
        r_min_angle = []
        
        for theta_deg in theta_angles:
            theta_rad = np.radians(theta_deg)
            atan2_vals = np.arctan2(y_work, x_work)
            mask_theta = np.abs(atan2_vals - theta_rad) < 0.12
            
            if np.any(mask_theta):
                r_angle = np.sqrt(x_work[mask_theta]**2 + y_work[mask_theta]**2)
                r_max_angle.append(np.max(r_angle))
                r_min_angle.append(np.min(r_angle))
            else:
                r_max_angle.append(np.nan)
                r_min_angle.append(np.nan)
        
        ax4.plot(theta_angles, r_max_angle, color='#FF6347', linewidth=2.5, label='R máximo')
        ax4.fill_between(theta_angles, r_min_angle, r_max_angle, alpha=0.25, color='#87CEEB')
        ax4.set_xlabel('Ángulo de Posición (grados)', fontsize=10, fontweight='bold')
        ax4.set_ylabel('Radio (unidades)', fontsize=10, fontweight='bold')
        ax4.set_title('Cobertura Radial por Ángulo', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.2, color='gray', linestyle=':')
        ax4.set_xlim(0, 360)
        ax4.set_facecolor('#ffffff')
        ax4.legend(fontsize=9, framealpha=0.95)
        
        fig.canvas.draw_idle()
        print("Dashboard actualizado.")
    
    # Conectar sliders
    slider_L1.on_changed(actualizar)
    slider_L2.on_changed(actualizar)
    slider_L3.on_changed(actualizar)
    
    # Actualización inicial
    actualizar(None)
    
    plt.subplots_adjust(left=0.1, right=0.95, top=0.93, bottom=0.2, hspace=0.35, wspace=0.3)
    plt.show()


if __name__ == "__main__":
    print("=" * 95)
    print("╔" + "=" * 93 + "╗")
    print("║" + " " * 15 + "BRAZO ROBÓTICO ANTROPOMÓRFICO 3DOF".center(63) + " " * 15 + "║")
    print("║" + " " * 15 + "Dashboard de Análisis de Workspace".center(63) + " " * 15 + "║")
    print("╚" + "=" * 93 + "╝")
    print("\nArquitectura del Brazo Antropomórfico:")
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │ L1: Brazo (Hombro - Codo)                      │")
    print("  │ L2: Antebrazo (Codo - Muñeca)                  │")
    print("  │ L3: Mano (Muñeca - Efector Final)              │")
    print("  │                                                 │")
    print("  │ Proporciones antropomórficas estándar          │")
    print("  └─────────────────────────────────────────────────┘")
    print("\nCaracterísticas:")
    print("  ✓ Visualización completa del espacio de trabajo para brazo 3DOF")
    print("  ✓ Simulación de brazo humanoides con articulaciones realistas")
    print("  ✓ Cálculo del casco convexo (límite exterior del workspace)")
    print("  ✓ Análisis de distribución radial")
    print("  ✓ Cobertura angular completa")
    print("  ✓ Proporciones antropomórficas ajustables")
    print("\nFórmulas de Cinemática Directa (3DOF):")
    print("  x = L1·cos(θ1) + L2·cos(θ1+θ2) + L3·cos(θ1+θ2+θ3)")
    print("  y = L1·sin(θ1) + L2·sin(θ1+θ2) + L3·sin(θ1+θ2+θ3)")
    print("\nControles Interactivos:")
    print("  • Slider L1 (Brazo):     Longitud del brazo superior")
    print("  • Slider L2 (Antebrazo): Longitud del antebrazo")
    print("  • Slider L3 (Mano):      Longitud de la mano/efector")
    print("\nVisualizaciones del Dashboard:")
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │ Panel Superior Izquierdo:  Workspace principal  │")
    print("  │ Panel Superior Derecho:    Estadísticas sistema │")
    print("  │ Panel Inferior Izquierdo:  Distribución radial  │")
    print("  │ Panel Inferior Derecho:    Cobertura angular    │")
    print("  └─────────────────────────────────────────────────┘")
    print("\nOptimizaciones:")
    print("  • Muestreo adaptativo para cálculo rápido con 3DOF")
    print("  • Interfaz mejorada con colores antropomórficos")
    print("  • Análisis en tiempo real al ajustar parámetros")
    print("\n" + "=" * 95 + "\n")
    
    crear_dashboard_workspace_3dof()
