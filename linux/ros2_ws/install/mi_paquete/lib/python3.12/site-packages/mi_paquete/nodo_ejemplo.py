import rclpy
from rclpy.node import Node

class NodoEjemplo(Node):
    def __init__(self):
        super().__init__('nodo_ejemplo')
        self.get_logger().info('Nodo iniciado correctamente')

def main(args=None):
    rclpy.init(args=args)
    nodo = NodoEjemplo()
    rclpy.spin(nodo)
    nodo.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
