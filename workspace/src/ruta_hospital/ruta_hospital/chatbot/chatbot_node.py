#!/usr/bin/env python3
import os
import json
import rclpy
from rclpy.node import Node
from workspace.src.ruta_hospital.ruta_hospital.utils.commons.api_utils import call_ollama_api
from hospital_interfaces.srv import GetPatrolContext
#from ament_index_python.packages import get_package_share_directory

from ruta_hospital.utils.shared.rag_utils import format_context_for_ragas, get_relevant_context
from ruta_hospital.reporting.utils.recursive_summarizer import RecursiveSummarizer

#PKG_DIR = get_package_share_directory('ruta_hospital')

DEFAULT_CONTEXT_FILE = "/home/alberto/tfg/Reconocimiento-y-sintesis-visual-Tiago/autogenerate_metrics/latest_patrol_context.json"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_CHAT_MODEL = "llama3" 
DEFAULT_HISTORY_LIMIT = 5
DEFAULT_WORD_LIMIT = 300
DEFAULT_INCLUDE_FINAL_SUMMARY = False

class PatrolChatbotNode(Node):
    def __init__(self):
        super().__init__('patrol_chatbot_node')
        self.declare_parameter('ollama_url', DEFAULT_OLLAMA_URL)
        self.declare_parameter('chat_model', DEFAULT_CHAT_MODEL)
        self.declare_parameter('context_file', DEFAULT_CONTEXT_FILE)
        self.declare_parameter('max_words', DEFAULT_WORD_LIMIT)
        self.declare_parameter('history_limit', DEFAULT_HISTORY_LIMIT)
        self.declare_parameter('include_final_summary', DEFAULT_INCLUDE_FINAL_SUMMARY)

        self.ollama_url = self.get_parameter('ollama_url').get_parameter_value().string_value
        self.chat_model = self.get_parameter('chat_model').get_parameter_value().string_value
        self.context_file = self.get_parameter('context_file').get_parameter_value().string_value
        self.max_words = self.get_parameter('max_words').get_parameter_value().integer_value
        self.history_limit = self.get_parameter('history_limit').get_parameter_value().integer_value
        self.include_final_summary = self.get_parameter('include_final_summary').get_parameter_value().bool_value

        self.context_data = self.get_context_hybrid()

    def get_context_hybrid(self):
        '''Intenta obtener contexto por servicio o por archivo'''
        client = self.create_client(GetPatrolContext, 'get_patrol_context')
        
        self.get_logger().debug("Intentando conectar con el Reportero")
        if client.wait_for_service(timeout_sec=2.0):
            req = GetPatrolContext.Request()
            future = client.call_async(req)
            # Terminal bloqueante, esperar el resultado
            rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
            res = future.result()
            if res and res.success:
                self.get_logger().info("Contexto recibido vía SERVICIO.")
                return {
                    "global_context": json.loads(res.global_context),
                    "final_summary": res.final_summary
                }
        
        self.get_logger().warn("Reportero no responde. Intentando carga desde ARCHIVO...")
        return self.load_context()

    def load_context(self):
        '''Carga el archivo JSON con los datos y el resumen de la última patrulla'''
        if not os.path.exists(self.context_file):
            return None
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.get_logger().error(f"Error leyendo {self.context_file}: {e}")
            return None

    def build_system_prompt(self):
        '''Construye el prompt base inyectando el RAG de la última vuelta'''
        if not self.context_data:
            return "Eres el asistente de seguridad del hospital. No tienes datos de patrullas recientes."
        
        base_prompt = """Eres una IA de reconocimiento de actividades humanas en un robot de patrulla del hospital. 
        El usuario te hará preguntas sobre la última patrulla realizada."""
        
        if self.include_final_summary:
            final_summary = self.context_data.get("final_summary", "")
            base_prompt += f"""\nA continuación tienes el resumen general de incidentes.
        RESUMEN FINAL:
        {final_summary}"""
        
        base_prompt += """\nSe te proporcionará información específica de los sensores (eventos) según lo que el usuario pregunte.
        Usa esa información para responder de forma concisa, directa y profesional.
        No inventes información que no esté en el contexto explícito. Si los datos indican que no hay actividad en una zona, dilo. Responde siempre en español."""

        return base_prompt

    def call_ollama(self, prompt):
        '''Wrapper para call_ollama_api'''
        payload = {
            "model": self.chat_model,
            "prompt": prompt,
            "stream": False
        }
        try:
            return call_ollama_api(self.ollama_url, payload).strip()
        except Exception as e:
            return f"Error de inferencia conectando a la API: {e}"

    def prepare_initial_context(self):
        '''Prepara el contexto natural completo a partir de los datos cargados'''
        if not self.context_data:
            print("AVISO: No se encontró el archivo de la última patrulla. Responderé sin contexto.")
            return []
        
        global_context_dict = self.context_data.get("global_context", {})
        global_context_json = json.dumps(global_context_dict, ensure_ascii=False)
        return format_context_for_ragas(global_context_json, filter_empty=False)

    def get_relevant_context_str(self, user_input, natural_context_full, base_prompt_words):
        '''Filtra y resume el contexto basándose en la entrada del usuario'''
        relevant_contexts = get_relevant_context(natural_context_full, user_input.lower())

        if relevant_contexts == natural_context_full:
            if not self.include_final_summary:
                # Resumen del LLM como fallback si RAG no encuentra la zona
                final_summary = self.context_data.get("final_summary", "No hay resumen disponible.")
                relevant_contexts = [final_summary]
            else:
                # Evitar duplicar el contexto
                relevant_contexts = ["Consulta el resumen final incluido en tus instrucciones."]

        context_str = "\n".join(relevant_contexts)

        available_words = self.max_words - base_prompt_words
        if available_words < 50:
            available_words = 50 # Mínimo vital para que el Summary Tree no crashee por escasez
            
        if len(context_str.split()) > available_words:
            try:
                print("Chatbot: Resumiendo registros extensos...", end="\r")
                summarizer = RecursiveSummarizer(
                    ollama_url=self.ollama_url,
                    model_name=self.chat_model,
                    logger=self.get_logger(),
                    max_words=available_words
                )
                context_str = summarizer.recursive_summarize(relevant_contexts, reduction_prompt)
            except Exception as e:
                self.get_logger().error(f"Error en summary trees chatbot: {e}")
                
        return context_str
    
    def format_history_to_str(self, history_list):
        '''Convierte la lista de diccionarios del historial en un texto plano'''
        text = ""
        for turn in history_list:
            text += f"\nUsuario: {turn['usuario']}\nAsistente: {turn['chatbot']}\n"
        return text

    def run_chat(self):
        '''Orquestador del bucle y la interfaz'''
        self.get_logger().info("Iniciando Interfaz de Chatbot...")
        print("\n" + "="*60)
        print("Chatbot: Pregúntame sobre la última ruta. Escribe 'salir' para terminar.")
        
        natural_context_full = self.prepare_initial_context()
        
        print("="*60 + "\n")

        system_prompt = self.build_system_prompt()
        chat_history = [] # Memoria de la conversación como sliding window

        while rclpy.ok():
            try:
                user_input = input("\nUsuario: ")
                if user_input.lower() in ['salir', 'exit', 'quit', 'q']:
                    print("Chatbot: Cerrando chat...")
                    break
                if not user_input.strip():
                    continue
                
                print("Chatbot: Analizando registros...", end="\r")

                history_str_base = self.format_history_to_str(chat_history)
                current_history_str = history_str_base + f"\nUsuario: {user_input}\n"

                # Pre-calcular el prompt sin contexto para contar sus palabras
                prompt_template = f"{system_prompt}\n\nDATOS RELEVANTES DE LOS SENSORES PARA ESTA PREGUNTA:\n\n\nHISTORIAL DE CONVERSACIÓN RECIENTE:{current_history_str}\nAsistente:"
                base_prompt_words = len(prompt_template.split())
                
                context_str = self.get_relevant_context_str(user_input, natural_context_full, base_prompt_words)

                # Inyección del contexto filtrado y construcción del prompt
                full_prompt = f"{system_prompt}\n\nDATOS RELEVANTES DE LOS SENSORES PARA ESTA PREGUNTA:\n{context_str}\n\nHISTORIAL DE CONVERSACIÓN RECIENTE:{current_history_str}\nAsistente:"
                
                print("Chatbot: Generando respuesta...       ", end="\r")
                response = self.call_ollama(full_prompt)
                
                chat_history.append({"usuario": user_input, "chatbot": response})
                if len(chat_history) > self.history_limit:
                    chat_history.pop(0) 
                
                print(" "*50, end="\r") # Limpiar la línea de "pensando"
                print(f"Chatbot: {response}")

            except (KeyboardInterrupt, EOFError):
                print("\nChatbot: Interrupción detectada. Cerrando chat...")
                break

def reduction_prompt(chunk):
    return f"Extrae de forma muy concisa los datos sobre actividades, personas o anomalías de este registro:\n{chunk}\nDatos extraídos:"

def main(args=None):
    rclpy.init(args=args)
    chatbot_node = PatrolChatbotNode()
    try:
        chatbot_node.run_chat()
    finally:
        chatbot_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()