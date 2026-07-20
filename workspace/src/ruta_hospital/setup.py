import os
from glob import glob
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
        (os.path.join('share', package_name, 'launch_files'), glob('launch_files/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.*')),
        (os.path.join('share', package_name, 'slam_maps'), glob('slam_maps/*.*')),
        (os.path.join('share', package_name, 'rviz_configs'), glob('rviz_configs/*.rviz')),
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
            'fotos = ruta_hospital.capturer.photos_capturer_node:main',
            'video_capturer_node = ruta_hospital.capturer.video_capturer_node:main',

            'yolo_perception_node = ruta_hospital.perception.yolo_perception_node:main',
            'vlm_perception_node = ruta_hospital.perception.vlm_perception_node:main',
            'sequence_perception_node = ruta_hospital.perception.sequence_perception_node:main',
            'hybrid_perception_node = ruta_hospital.perception.hybrid_perception_node:main',
            'video_perception_node = ruta_hospital.perception.video_perception_node:main',

            'llm_reporter_node = ruta_hospital.reporting.llm_reporter_node:main',
            'vlm_direct_reporter_node = ruta_hospital.reporting.vlm_direct_reporter_node:main',

            'system_evaluator_node = ruta_hospital.evaluation.system_evaluator_node:main',
            'perception_evaluator_node = ruta_hospital.evaluation.perception_evaluator_node:main',

            'alarm_notifier_node = ruta_hospital.alarm.alarm_notifier_node:main',
        ],
    },
)
