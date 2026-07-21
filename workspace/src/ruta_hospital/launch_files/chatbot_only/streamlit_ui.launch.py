import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    pkg_dir = get_package_share_directory('ruta_hospital')
    
    chatbot_ui_cmd = ExecuteProcess(
        cmd=['gnome-terminal', '--', 'bash', '-c', 'streamlit run src/ruta_hospital/ruta_hospital/chatbot/chatbot_web.py -- --use-reranker; exec bash'],
        output='screen'
    )

    ld = LaunchDescription()
    ld.add_action(chatbot_ui_cmd)

    return ld