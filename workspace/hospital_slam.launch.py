import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # RUTAS
    home_dir = os.path.expanduser('~')
    workspace_path = os.path.join(home_dir, 'tfg/Reconocimiento-y-sintesis-visual-Tiago/workspace')
    
    # Rutas a los modelos del hospital (AWS)
    hospital_models = os.path.join(workspace_path, 'src/aws-robomaker-hospital-world/models')
    hospital_fuel = os.path.join(workspace_path, 'src/aws-robomaker-hospital-world/fuel_models')
    
    # Archivo de params de SLAM
    slam_params_file = os.path.join(workspace_path, 'hospital_slam_params.yaml')

    # VARIABLES DE ENTORNO
    set_model_path = AppendEnvironmentVariable(
        'GAZEBO_MODEL_PATH',
        str(hospital_models) + ':' + str(hospital_fuel)
    )

    # RELAY de /scan_raw a /scan (el robot no publica en /scan)
    relay_node = Node(
        package='topic_tools',
        executable='relay',
        name='scan_relay',
        arguments=['/scan_raw', '/scan'],
        output='screen'
    )

    # GAZEBO
    tiago_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('tiago_gazebo'),
                'launch',
                'tiago_gazebo.launch.py'
            ])
        ]),
        launch_arguments={
            'is_public_sim': 'True',
            'world_name': 'hospital',
            'arm_type': 'no-arm', # Sin brazo
            'moveit': 'False'
        }.items()
    )

    # SLAM TOOLBOX sincrono
    slam_node = Node(
        package='slam_toolbox',
        executable='sync_slam_toolbox_node',
        name='slam_toolbox', # hace el remapping de __node automáticamente
        output='screen',
        parameters=[slam_params_file]
    )

    # NAV2
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': 'True',
            'params_file': PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'params',
                'nav2_params.yaml'
            ])
        }.items()
    )

    # RVIZ
    rviz_config_path = os.path.join(workspace_path, 'rviz_configs/slam_config.rviz')
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        output='screen'
    )

    # ANTI-SPIN para intentar reducir los fallos al girar
    apply_params = TimerAction(
        period=5.0, # 5 segundos de espera para que Nav2 arranque
        actions=[
            ExecuteProcess( # para simular el comando de terminal
                cmd=['ros2', 'param', 'set', '/controller_server', 'FollowPath.min_vel_x', '0.1'],
                output='screen'
            ),
            ExecuteProcess(
                cmd=['ros2', 'param', 'set', '/controller_server', 'FollowPath.max_vel_theta', '0.4'],
                output='screen'
            ),
            ExecuteProcess(
                cmd=['ros2', 'param', 'set', '/controller_server', 'FollowPath.min_speed_xy', '0.1'],
                output='screen'
            ),
            ExecuteProcess(
                cmd=['ros2', 'param', 'set', '/controller_server', 'FollowPath.acc_lim_theta', '0.5'],
                output='screen'
            )
        ]
    )

    # TELEOP (es necesario tener gnome-terminal instalado, es la por defecto en Ubuntu)
    teleop_node = ExecuteProcess(
        cmd=['gnome-terminal', '--', 'ros2', 'run', 'teleop_twist_keyboard', 'teleop_twist_keyboard'],
        output='screen'
    )

    return LaunchDescription([
        set_model_path,
        relay_node,
        tiago_gazebo,
        slam_node,
        nav2_launch,
        rviz_node,
        apply_params,
        teleop_node
    ])