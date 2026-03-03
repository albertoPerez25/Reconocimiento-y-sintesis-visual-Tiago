from setuptools import find_packages, setup

package_name = 'ruta_hospital'

setup(
    name=package_name,
    version='0.0.2',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='alberto',
    maintainer_email='alberto.perez25@alu.uclm.es',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'patrulla = ruta_hospital.navigation.patrol_node:main',
            'fotos = ruta_hospital.perception.photos_node:main',

            'yolo_perception_node = ruta_hospital.perception.yolo_perception_node:main',
            'vlm_perception_node = ruta_hospital.perception.vlm_perception_node:main',
            'sequence_perception_node = ruta_hospital.perception.sequence_perception_node:main',
            'hybrid_perception_node = ruta_hospital.perception.hybrid_perception_node:main',

            'llm_reporter_node = ruta_hospital.reporting.llm_reporter_node:main',
            'vlm_direct_reporter_node = ruta_hospital.reporting.vlm_direct_reporter_node:main',
        ],
    },
)
