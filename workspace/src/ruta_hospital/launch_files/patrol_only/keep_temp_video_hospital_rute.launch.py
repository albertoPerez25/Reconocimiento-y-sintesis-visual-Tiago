import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess

def generate_launch_description():
    # Ruta donde está este paquete
    pkg_dir = get_package_share_directory('ruta_hospital')

    # Rutas dinámicas apuntando a las carpetas instaladas
    map_path = os.path.join(pkg_dir, 'slam_maps', 'hospital.yaml')
    nav2_params_path = os.path.join(pkg_dir, 'config', 'nav2_params.yaml') 
    ekf_params_path = os.path.join(pkg_dir, 'config', 'ekf.yaml')
    rviz_config_path = os.path.join(pkg_dir, 'rviz_configs', 'slam_config.rviz')


    # Configuración de rutas para modelos de Gazebo
    home_dir = os.path.expanduser('~')
    workspace_path = os.path.join(home_dir, 'tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace')
    hospital_models = os.path.join(workspace_path, 'src/aws-robomaker-hospital-world/models')
    hospital_fuel = os.path.join(workspace_path, 'src/aws-robomaker-hospital-world/fuel_models')
    
    set_model_path = AppendEnvironmentVariable(
        'GAZEBO_MODEL_PATH',
        f"{hospital_models}:{hospital_fuel}:{os.path.expanduser('~/.gazebo/models')}"
    )

    # Gazebo sin brazo
    tiago_gazebo_dir = get_package_share_directory('tiago_gazebo')
    gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(tiago_gazebo_dir, 'launch', 'tiago_gazebo.launch.py')),
        launch_arguments={
            'is_public_sim': 'True',
            'world_name': 'hospital',
            'arm_type': 'no-arm',
            'gui': 'False'
        }.items()
    )

    # RViz2
    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Nav2
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'use_sim_time': 'True',
            'map': map_path,
            'params_file': nav2_params_path
        }.items()
    )

    # Nodo Relay (topic_tools)
    relay_cmd = Node(
        package='topic_tools',
        executable='relay',
        name='scan_relay',
        arguments=['/scan_raw', '/scan'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Nodo EKF (para la odometría e IMU)
    ekf_cmd = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        parameters=[ekf_params_path, {'use_sim_time': True}],
        remappings=[('odometry/filtered', '/odom')],
        output='screen'
    )

    # Nodo Patrulla 
    patrulla_cmd = TimerAction(
        period=27.0,
        actions=[
            Node(
                package='ruta_hospital',
                executable='patrulla', # TODO: Nombre genérico
                name='patrol_node',
                parameters=[{
                    'use_sim_time': True,
                    'keep_temp_folders': True,
                    'capturer_node_name': 'video_capturer_node',
                    'use_reranker': True
                }],
                output='screen',
                prefix='gnome-terminal -- ' # para que salga en otra terminal
            )
        ]
    )
    
    # Nodo Capturador de Vídeo en terminal independiente
    video_cmd = TimerAction(
        period=25.0,
        actions=[
            Node(
                package='ruta_hospital',
                executable='video_capturer_node', 
                name='video_capturer_node', 
                parameters=[{'use_sim_time': True,
                             'capture_mode':'video'}],
                output='screen',
                prefix='gnome-terminal -- ' 
            )
        ]
    )


    # Como PAL Robotics filtra el argumento 'gui', gzclient se abrirá.
    # Esta rutina lo detecta y lo mata a los 8 segundos de arrancar, 
    # liberando de 1 a 2 GB de VRAM instantáneamente, pero dejando 
    # a gzserver intacto para que las cámaras del robot sigan viendo.
    headless_enforcer = TimerAction(
        period=8.0, 
        actions=[
            ExecuteProcess(
                cmd=['killall', '-9', 'gzclient'],
                output='screen'
            )
        ]
    )

    # Descripcion del Launch
    ld = LaunchDescription()
    ld.add_action(set_model_path)
    ld.add_action(gazebo_cmd)
    #ld.add_action(headless_enforcer)
    ld.add_action(relay_cmd)
    ld.add_action(ekf_cmd)
    ld.add_action(nav2_cmd)
    ld.add_action(rviz_cmd)
    ld.add_action(patrulla_cmd)
    ld.add_action(video_cmd) 

    return ld