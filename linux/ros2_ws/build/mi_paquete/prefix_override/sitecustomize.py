import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/darka/Uni/linux/ros2_ws/install/mi_paquete'
