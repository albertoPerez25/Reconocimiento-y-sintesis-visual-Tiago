import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess, AppendEnvironmentVariable
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

    # Configuración de rutas para modelos de Gazebo
    home_dir = os.path.expanduser('~')
    workspace_path = os.path.join(home_dir, 'tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace')
    hospital_models = os.path.join(workspace_path, 'src/aws-robomaker-hospital-world/models')
    hospital_fuel = os.path.join(workspace_path, 'src/aws-robomaker-hospital-world/fuel_models')
    
    set_model_path = AppendEnvironmentVariable(
        'GAZEBO_MODEL_PATH',
        f"{hospital_models}:{hospital_fuel}:{os.path.expanduser('~/.gazebo/models')}"
    )

    # Gazebo sin brazo (Modo Headless para ahorrar recursos y evitar fallos del gui)
    tiago_gazebo_dir = get_package_share_directory('tiago_gazebo')
    gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(tiago_gazebo_dir, 'launch', 'tiago_gazebo.launch.py')),
        launch_arguments={
            'is_public_sim': 'True',
            'world_name': 'hospital',
            'arm_type': 'no-arm',
            'gui': 'False' # Desactiva el cliente de gazebo para ahorrar recursos
        }.items()
    )

    # RViz2 (Monitorización visual)
    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Nav2 (Stack de Navegación)
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'use_sim_time': 'True',
            'map': map_path,
            'params_file': nav2_params_path
        }.items()
    )

    # Nodo Relay (topic_tools) para mapear /scan_raw a /scan
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

    # Nodo Patrulla (Orquestador de movimiento)
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
                    'capturer_node_name': 'video_capturer_node',
                    'use_reranker': True
                }],
                output='screen',
                prefix='gnome-terminal -- ' # Abre en nueva terminal
            )
        ]
    )
    
    # Nodo Capturador de Vídeo (Extrae secuencias de la cámara)
    video_cmd = TimerAction(
        period=25.0,
        actions=[
            Node(
                package='ruta_hospital',
                executable='video_capturer_node', 
                name='video_capturer_node', 
                parameters=[{'use_sim_time': True, 
                    'capture_mode': 'video'}], # por consistencia, no hace falta
                output='screen',
                prefix='gnome-terminal -- ' 
            )
        ]
    )
    
    # Orquestador SOTA (Patrón Strategy) -> Nodo Híbrido en modo vídeo
    hybrid_perception_cmd = TimerAction(
        period=27.0,
        actions=[
            Node(
                package='ruta_hospital',
                executable='hybrid_perception_node',
                name='hybrid_perception_node',
                parameters=[{
                    'use_sim_time': True,
                    'vlm_estimators': ['ruta_hospital.perception.video_perception_node.VideoPerceptionNode']
                }],
                output='screen',
                prefix='gnome-terminal -- '
            )
        ]
    )

    # Orquestador Cognitivo (RAG y Consolidación de información)
    llm_reporter_cmd = TimerAction(
        period=30.0,
        actions=[
            Node(
                package='ruta_hospital',
                executable='llm_reporter_node',
                name='llm_reporter_node',
                parameters=[{'use_sim_time': True, 'perception_mode': 'video'}],
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


    # Como PAL Robotics filtra el argumento 'gui', gzclient se abrirá igual.
    # Esta rutina lo detecta y lo mata a los 8 segundos de arrancar, 
    # liberando VRAM instantáneamente (gzserver sigue intacto).
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
    ld.add_action(hybrid_perception_cmd)
    ld.add_action(llm_reporter_cmd)
    ld.add_action(chatbot_ui_cmd)

    return ld