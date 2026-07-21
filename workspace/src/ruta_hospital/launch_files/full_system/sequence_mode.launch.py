import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # Ruta donde está este paquete
    pkg_dir = get_package_share_directory('ruta_hospital')

    # Rutas dinámicas apuntando a las carpetas instaladas
    map_path = os.path.join(pkg_dir, 'slam_maps', 'hospital.yaml')
    nav2_params_path = os.path.join(pkg_dir, 'config', 'nav2_params.yaml') 
    ekf_params_path = os.path.join(pkg_dir, 'config', 'ekf.yaml')
    rviz_config_path = os.path.join(pkg_dir, 'rviz_configs', 'slam_config.rviz')

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

    # Nodo EKF (Fusión de Odometría e IMU)
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
        period=35.0,
        actions=[
            Node(
                package='ruta_hospital',
                executable='patrulla', 
                name='patrol_node',
                parameters=[{
                    'use_sim_time': True,
                    'keep_temp_folders': True,
                    'capturer_node_name': 'fotos',
                    'use_reranker': True
                }],
                output='screen',
                prefix='gnome-terminal -- ' 
            )
        ]
    )
    
    # Nodo Capturador de Fotos (Modificado a secuencia)
    fotos_cmd = TimerAction(
        period=25.0,
        actions=[
            Node(
                package='ruta_hospital',
                executable='fotos',
                name='photos_node',
                parameters=[{'use_sim_time': True, 'capture_mode': 'sequence'}],
                output='screen',
                prefix='gnome-terminal -- ' 
            )
        ]
    )
    
    # Orquestador SOTA (Patrón Strategy) -> Nodo Híbrido inyectando el perceptor de secuencia
    hybrid_perception_cmd = TimerAction(
        period=27.0,
        actions=[
            Node(
                package='ruta_hospital',
                executable='hybrid_perception_node',
                name='hybrid_perception_node',
                parameters=[{
                    'use_sim_time': True,
                    'vlm_estimators': ['ruta_hospital.perception.sequence_perception_node.SequencePerceptionNode']
                }],
                output='screen',
                prefix='gnome-terminal -- '
            )
        ]
    )

    # Orquestador Cognitivo (RAG y Consolidación de información) -> Modo secuencia
    llm_reporter_cmd = TimerAction(
        period=30.0,
        actions=[
            Node(
                package='ruta_hospital',
                executable='llm_reporter_node',
                name='llm_reporter_node',
                parameters=[{'use_sim_time': True, 'perception_mode': 'sequence'}],
                output='screen',
                prefix='gnome-terminal -- '
            )
        ]
    )
    
    # Interfaz Interactiva de Usuario (Streamlit)
    chatbot_ui_cmd = TimerAction(
        period=35.0,
        actions=[
            ExecuteProcess(
                cmd=['gnome-terminal', '--', 'bash', '-c', 'streamlit run src/ruta_hospital/ruta_hospital/chatbot/chatbot_web.py -- --use-reranker; exec bash'],
                output='screen'
            )
        ]
    )

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
    ld.add_action(gazebo_cmd)
    #ld.add_action(headless_enforcer)
    ld.add_action(relay_cmd)
    ld.add_action(ekf_cmd)
    ld.add_action(nav2_cmd)
    ld.add_action(rviz_cmd)
    ld.add_action(patrulla_cmd)
    ld.add_action(fotos_cmd)
    ld.add_action(hybrid_perception_cmd)
    ld.add_action(llm_reporter_cmd)
    ld.add_action(chatbot_ui_cmd)

    return ld
