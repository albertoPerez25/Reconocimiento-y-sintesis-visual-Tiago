import json
import re

def format_context_for_ragas(json_context, filter_empty=False): # NO USADA, eliminado su uso en la estandarización de RAG. 
                                                                # TODO: Puede ser interesante comparar contexto RAW vs natural
    '''Convierte el JSON de los perceptores en lenguaje natural para que RAGAS lo entienda'''
    try:
        data = json.loads(json_context)
        formatted_contexts = []
        
        if isinstance(data, dict) and any(isinstance(v, dict) for v in data.values()): #el json esta dividido en zonas
            for zone, info in data.items():
                events = info.get("eventos_recientes", [])
                if not events:
                    if not filter_empty:
                        formatted_contexts.append(f"La zona '{zone}' está despejada, sin eventos ni personas.")
                else:
                    for ev in events:
                        desc = ev.get("descripcion_vlm", "sin descripción")
                        detection = "Se ha detectado actividad humana" if ev.get("alerta") else "No hay alertas ni peligros" # TODO
                        formatted_contexts.append(f"En la zona '{zone}': {desc}. {detection}.")
        

        if not formatted_contexts:
            return ["El entorno está completamente despejado y sin incidencias."]
            
        return formatted_contexts
    except Exception:
        # texto plano encapsulado en una lista (lo que espera RAGAS)
        return [str(json_context).strip()]
    
def get_relevant_context(natural_language_context, question_lower):
    '''Filtra el contexto y devuelve solo la zona relevante para facilitar el trabajo a RAGAS'''
    relevant_contexts = []
    for chunk in natural_language_context:
        match = re.search(r"'(.*?)'", chunk)
        if match:
            complete_zone = match.group(1).lower()
            # Cosas como "Recepción (cerca de X)"
            base_zone = complete_zone.split(" (")[0] 
            
            if base_zone in question_lower or complete_zone in question_lower:
                relevant_contexts.append(chunk)
    
    if not relevant_contexts:
        relevant_contexts = natural_language_context

    return relevant_contexts