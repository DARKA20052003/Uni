from setuptools import setup, find_packages

package_name = 'mi_paquete'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='darka',
    maintainer_email='ad.darquea.cing@uteg.edu.ec',
    description= 'Nodo de prueba de ROS2 (Humble)',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'nodo = mi_paquete.nodo_ejemplo:main'
        ],
    },
)
