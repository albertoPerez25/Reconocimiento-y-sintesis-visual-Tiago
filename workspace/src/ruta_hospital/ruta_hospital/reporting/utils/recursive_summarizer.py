from workspace.src.ruta_hospital.ruta_hospital.utils.commons.api_utils import call_ollama_api

class RecursiveSummarizer:
    def __init__(self, ollama_url, model_name, logger, max_words=800):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.logger = logger
        self.max_words = max_words
        self.final_context = ""

    def count_words(self, text):
        '''Cuenta las palabras de un texto'''
        return len(str(text).split())

    def summarize_chunk(self, chunk_text):
        '''Resume un lote intermedio manteniendo los datos críticos'''
        prompt = f"""
        Eres una IA de análisis de actividades humanas. Resume BREVEMENTE el siguiente reporte parcial de actividades del hospital.
        MANTÉN todos los detalles críticos: actividades humanas, personas caídas o incumplimientos.
        No inventes datos. Si una zona no tiene nada relevante, omítela.

        Reporte Parcial:
        {chunk_text}
        
        Resumen Parcial:
        """
        try:
            return call_ollama_api(self.ollama_url, {"model": self.model_name, "prompt": prompt, "stream": False})
        except Exception as e:
            self.logger.error(f"Error resumiendo lote: {e}")
            return ""

    def recursive_summarize(self, text_zones, final_prompt_func):
        ''' Algoritmo Recursivo (Tree of Summaries):
        Agrupa los textos en lotes según el límite establecido. Si cabe en 1 lote, hace el reporte final, 
        si no, resume cada lote y se llama a si mismo con los nuevos resúmenes'''
        combined_text = "\n\n".join(text_zones)
        
        # si el lote es menor al límite solo se debe hacer una llamada
        if self.count_words(combined_text) <= self.max_words: 
            self.logger.info("Generando resumen final...")
            self.final_context = combined_text
            prompt = final_prompt_func(combined_text)
            return call_ollama_api(self.ollama_url, {"model": self.model_name, "prompt": prompt, "stream": False})

        self.logger.info("El contexto supera el límite. Se hará reducción jerárquica...")
        processed_new_text_chunks = self.map_aggrupation(text_zones)

        self.logger.debug("Lotes intermedios completados. Subiendo de nivel...")
        return self.recursive_summarize(processed_new_text_chunks, final_prompt_func)
    
    def map_aggrupation(self, text_zones):
        '''Agrupa los textos de las zonas en fragmentos que no superen el límite de palabras'''
        processed_new_text_chunks = []
        current_text_chunk = []
        current_n_words = 0

        for text in text_zones:
            n_words = self.count_words(text)
            
            # En caso de que no quepa un lote entero, se deja pendiente para el siguiente
            if current_n_words + n_words > self.max_words and current_text_chunk:
                processed_new_text_chunks = self.process_current_chunk(
                    current_text_chunk, 
                    current_n_words, 
                    processed_new_text_chunks
                )

                current_text_chunk = [text]
                current_n_words = n_words
            else:
                current_text_chunk.append(text)
                current_n_words += n_words
        
        # ultimo lote
        if current_text_chunk:
            processed_new_text_chunks = self.process_current_chunk(
                    current_text_chunk, 
                    current_n_words, 
                    processed_new_text_chunks
                )

        return processed_new_text_chunks

    def process_current_chunk(self, current_text_chunk, current_n_words, new_text_chunks):
        '''Procesa el lote actual de textos, lo resume y lo añade a la lista de nuevos fragmentos'''
        chunk_str = "\n\n".join(current_text_chunk)
        self.logger.info(f"  - Procesando lote de {current_n_words} palabras")
        new_text_chunks.append(self.summarize_chunk(chunk_str))
        return new_text_chunks