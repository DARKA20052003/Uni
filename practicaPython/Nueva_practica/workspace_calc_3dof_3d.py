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
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.colors as mcolors

try:
    from scipy.spatial import ConvexHull
    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False


def rot_z(theta):
    c = np.cos(theta); s = np.sin(theta)
    R = np.array([[c, -s, 0, 0],
                  [s,  c, 0, 0],
                  [0,  0, 1, 0],
                  [0,  0, 0, 1]])
    return R


def rot_y(theta):
    c = np.cos(theta); s = np.sin(theta)
    R = np.array([[ c, 0, s, 0],
                  [ 0, 1, 0, 0],
                  [-s, 0, c, 0],
                  [ 0, 0, 0, 1]])
    return R


def trans_x(a):
    T = np.eye(4)
    T[0, 3] = a
    return T


class Workspace3DAnthro:
    """Calculadora de workspace 3D para un brazo antropomórfico 3DOF.

    Cinemática directa basada en transformaciones homogéneas:
    T = Rz(theta1) * Ry(theta2) * TransX(L1) * Ry(theta3) * TransX(L2) * TransX(L3)
    El efector final se obtiene aplicando T al origen.
    """

    def __init__(self, L1=1.4, L2=1.2, L3=0.9, n1=60, n2=30, n3=30):
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.points = None

    def forward(self, theta1, theta2, theta3):
        # Construir transformada homogénea acumulada
        T = rot_z(theta1) @ rot_y(theta2) @ trans_x(self.L1) @ rot_y(theta3) @ trans_x(self.L2) @ trans_x(self.L3)
        p = T @ np.array([0.0, 0.0, 0.0, 1.0])
        return p[:3]

    def compute_workspace(self):
        th1 = np.linspace(0, 2*np.pi, self.n1)
        # limitar pitch para simular hombro antropomórfico
        th2 = np.linspace(-np.pi/2, np.pi/2, self.n2)
        # limitar flexión de codo
        th3 = np.linspace(0, np.pi, self.n3)

        pts = []
        for t1 in th1:
            for t2 in th2:
                for t3 in th3[::2]:  # muestreo reducido para rapidez
                    p = self.forward(t1, t2, t3)
                    pts.append(p)
        pts = np.array(pts)
        self.points = pts
        return pts

    def stats(self):
        if self.points is None:
            self.compute_workspace()
        r = np.linalg.norm(self.points, axis=1)
        return {
            'num': len(self.points),
            'r_max': float(np.max(r)),
            'r_min': float(np.min(r)),
            'x_min': float(np.min(self.points[:,0])),
            'x_max': float(np.max(self.points[:,0])),
            'y_min': float(np.min(self.points[:,1])),
            'y_max': float(np.max(self.points[:,1])),
            'z_min': float(np.min(self.points[:,2])),
            'z_max': float(np.max(self.points[:,2])),
            'volume_hull': self._hull_volume() if SCIPY_AVAILABLE else None
        }

    def _hull_volume(self):
        try:
            hull = ConvexHull(self.points)
            return float(hull.volume)
        except Exception:
            return None


def crear_dashboard_3d():
    calc = Workspace3DAnthro()

    print('Calculando puntos del workspace 3D...')
    pts = calc.compute_workspace()
    print(f'Puntos calculados: {len(pts)}')

    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(111, projection='3d')
    fig.suptitle('Workspace 3D - Brazo Antropomórfico 3DOF (gráfica espacial)', fontsize=14)

    # Scatter 3D
    scat = ax.scatter(pts[:,0], pts[:,1], pts[:,2], c=pts[:,2], cmap='viridis', s=4, alpha=0.6)
    cb = fig.colorbar(scat, shrink=0.6, aspect=20, pad=0.1)
    cb.set_label('Altura Z')

    # Marcar base
    ax.scatter([0],[0],[0], color='k', s=60, label='Hombro (Base)')

    # Ajustes visuales
    alcance = calc.L1 + calc.L2 + calc.L3
    ax.set_xlim(-alcance, alcance)
    ax.set_ylim(-alcance, alcance)
    ax.set_zlim(0, alcance)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.legend(loc='upper left')
    ax.view_init(elev=25, azim=45)

    # Intentar dibujar casco convexo 3D si scipy está disponible
    hull_collection = None
    if SCIPY_AVAILABLE:
        try:
            hull = ConvexHull(pts)
            faces = [pts[simplex] for simplex in hull.simplices]
            hull_collection = Poly3DCollection(faces, alpha=0.15, facecolor='orange')
            ax.add_collection3d(hull_collection)
        except Exception as e:
            print('No se pudo calcular casco 3D:', e)

    # Panel lateral con estadísticas + controles
    ax_pos = plt.axes([0.02, 0.55, 0.18, 0.35])
    ax_pos.axis('off')
    info_text = ax_pos.text(0, 1, '', va='top', family='monospace')

    ax_slider_L1 = plt.axes([0.02, 0.38, 0.18, 0.03])
    ax_slider_L2 = plt.axes([0.02, 0.32, 0.18, 0.03])
    ax_slider_L3 = plt.axes([0.02, 0.26, 0.18, 0.03])
    ax_check = plt.axes([0.02, 0.18, 0.18, 0.06])

    sL1 = Slider(ax_slider_L1, 'L1 (Brazo)', 0.5, 2.5, valinit=calc.L1)
    sL2 = Slider(ax_slider_L2, 'L2 (Antebrazo)', 0.4, 2.5, valinit=calc.L2)
    sL3 = Slider(ax_slider_L3, 'L3 (Mano)', 0.2, 1.5, valinit=calc.L3)

    check = CheckButtons(ax_check, ['Mostrar casco 3D'], [SCIPY_AVAILABLE and hull_collection is not None])

    def refresh(val=None):
        calc.L1 = float(sL1.val)
        calc.L2 = float(sL2.val)
        calc.L3 = float(sL3.val)
        calc.points = None
        pts_new = calc.compute_workspace()

        # actualizar scatter
        scat._offsets3d = (pts_new[:,0], pts_new[:,1], pts_new[:,2])
        scat.set_array(pts_new[:,2])

        # actualizar limites
        alcance = calc.L1 + calc.L2 + calc.L3
        ax.set_xlim(-alcance, alcance)
        ax.set_ylim(-alcance, alcance)
        ax.set_zlim(0, alcance)

        # actualizar hull
        nonlocal hull_collection
        if SCIPY_AVAILABLE:
            try:
                if hull_collection is not None:
                    ax.collections.remove(hull_collection)
                hull = ConvexHull(pts_new)
                faces = [pts_new[simplex] for simplex in hull.simplices]
                hull_collection = Poly3DCollection(faces, alpha=0.12, facecolor='orange')
                if check.get_status()[0]:
                    ax.add_collection3d(hull_collection)
            except Exception as e:
                hull_collection = None

        st = calc.stats()
        info = f"L1={calc.L1:.2f}  L2={calc.L2:.2f}  L3={calc.L3:.2f}\n" \
               f"Puntos: {st['num']}\nR_max: {st['r_max']:.3f}  R_min: {st['r_min']:.3f}\n" \
               f"X: [{st['x_min']:.3f}, {st['x_max']:.3f}]\n" \
               f"Y: [{st['y_min']:.3f}, {st['y_max']:.3f}]\n" \
               f"Z: [{st['z_min']:.3f}, {st['z_max']:.3f}]\n" \
               f"Vol hull: {st['volume_hull'] if st['volume_hull'] is not None else 'N/A'}"
        info_text.set_text(info)
        fig.canvas.draw_idle()

    def on_check(label):
        if not SCIPY_AVAILABLE:
            return
        status = check.get_status()[0]
        if hull_collection is None:
            return
        if status:
            ax.add_collection3d(hull_collection)
        else:
            try:
                ax.collections.remove(hull_collection)
            except Exception:
                pass
        fig.canvas.draw_idle()

    sL1.on_changed(refresh)
    sL2.on_changed(refresh)
    sL3.on_changed(refresh)
    check.on_clicked(on_check)

    refresh()
    plt.subplots_adjust(left=0.23, right=0.97, top=0.92, bottom=0.05)
    plt.show()


if __name__ == '__main__':
    print('Dashboard 3D: Brazo antropomórfico 3DOF')
    if not SCIPY_AVAILABLE:
        print('Nota: SciPy no encontrado — casco convexo 3D deshabilitado')
    crear_dashboard_3d()
