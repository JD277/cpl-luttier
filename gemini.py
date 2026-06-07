import google.generativeai as genai
from typing import Optional, Union, List, Dict, Any


class GeminiManager:
    """
    Gestor centralizado para interacciones con la API de Google Gemini.
    
    Características:
    - Carga automática de API Key desde variables de entorno
    - Soporte para modelos de texto y visión (imágenes)
    - Manejo de historial de conversación (chat)
    - Configuración flexible de parámetros (temperature, max_tokens, etc.)
    - Logging integrado para debugging
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "text",
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        top_p: float = 0.95,
        top_k: int = 40,
        system_instruction: Optional[str] = None
    ):
        """
        Inicializa el gestor de Gemini.
        
        Args:
            api_key: Clave API de Google AI Studio. Si es None, se busca en 
                     variable de entorno GEMINI_API_KEY
            model_name: Nombre del modelo o clave del diccionario MODELS
            temperature: Creatividad (0.0 = determinista, 1.0 = creativo)
            max_output_tokens: Máximo de tokens en la respuesta
            top_p: Muestreo por núcleo (diversidad)
            top_k: Muestreo por top-k
            system_instruction: Instrucción del sistema para definir rol/comportamiento
        """

        
        # Resolver API Key
        self.api_key = api_key
        if not self.api_key:
            raise ValueError(
                "API Key no proporcionada. Pásala como argumento o configura "
                "la variable de entorno GEMINI_API_KEY"
            )
        
        # Configurar SDK
        genai.configure(api_key=self.api_key)
        
        # Resolver nombre real del modelo
        self.model_name = model_name
        
        # Configuración de generación
        self.generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            top_k=top_k
        )
        
        # Safety settings (opcional: relajar filtros si es necesario)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # Estado interno
        self._chat_session = None
        self._system_instruction = system_instruction
        
        print(f"[GeminiManager] Inicializado con modelo: {self.model_name}")
    
    # ------------------------------------------------------------------ #
    #                        CONSULTA SIMPLE                             #
    # ------------------------------------------------------------------ #
    def ask(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        mime_type: str = "image/jpeg"
    ) -> str:
        """
        Realiza una consulta simple (sin historial).
        
        Args:
            prompt: Texto de la pregunta/instrucción
            image_path: Ruta a imagen (opcional, activa modo visión)
            mime_type: Tipo MIME de la imagen
            
        Returns:
            Respuesta en texto plano
        """
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                system_instruction=self._system_instruction
            )
            
            # Construir contenido
            contents: List[Union[str, Dict]] = [prompt]
            if image_path:
                image_data = genai.upload_file(image_path, mime_type=mime_type)
                contents.append(image_data)
            
            response = model.generate_content(contents)
            
            # Validar respuesta
            if not response.text:
                return "[Gemini] La respuesta está vacía. Revisa safety settings."
            
            return response.text.strip()
            
        except Exception as e:
            error_msg = f"[GeminiManager] Error en ask(): {type(e).__name__}: {e}"
            print(error_msg)
            return f"Error: {error_msg}"
    
    # ------------------------------------------------------------------ #
    #                     CHAT CON HISTORIAL                             #
    # ------------------------------------------------------------------ #
    def start_chat(self, history: Optional[List[Dict[str, str]]] = None) -> None:
        """
        Inicia o reinicia una sesión de chat con historial.
        
        Args:
            history: Lista de mensajes previos [{"role": "user", "parts": "..."}]
        """
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            system_instruction=self._system_instruction
        )
        
        self._chat_session = model.start_chat(history=history or [])
        print("[GeminiManager] Sesión de chat iniciada")
    
    def send_message(self, message: str) -> str:
        """
        Envía un mensaje en la sesión de chat activa.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Respuesta del modelo
        """
        if self._chat_session is None:
            self.start_chat()
        
        try:
            response = self._chat_session.send_message(message)
            
            return response.candidates[0].content.parts[1]
        except Exception as e:
            error_msg = f"[GeminiManager] Error en send_message(): {e}"
            print(error_msg)
            return f"Error: {error_msg}"
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Retorna el historial completo de la conversación actual."""
        if self._chat_session is None:
            return []
        return [
            {"role": msg.role, "parts": msg.parts[0].text if msg.parts else ""}
            for msg in self._chat_session.history
        ]
    
    def clear_chat(self) -> None:
        """Limpia el historial y reinicia la sesión."""
        self._chat_session = None
        print("[GeminiManager] Historial de chat limpiado")
    
    # ------------------------------------------------------------------ #
    #                          UTILIDADES                                #
    # ------------------------------------------------------------------ #
    def list_models(self) -> List[str]:
        """Lista todos los modelos disponibles para tu API Key."""
        try:
            return [m.name for m in genai.list_models()]
        except Exception as e:
            print(f"[GeminiManager] Error listando modelos: {e}")
            return []
    
    def update_config(self, **kwargs) -> None:
        """
        Actualiza parámetros de generación en caliente.
        
        Ejemplo: gemini.update_config(temperature=0.2, max_output_tokens=4096)
        """
        valid_params = {"temperature", "max_output_tokens", "top_p", "top_k"}
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self.generation_config, key, value)
                print(f"[GeminiManager] {key} actualizado a {value}")
            else:
                print(f"[GeminiManager] Parámetro ignorado: {key}")
    
    def __repr__(self) -> str:
        return (
            f"GeminiManager(model={self.model_name}, "
            f"temp={self.generation_config.temperature}, "
            f"chat_active={self._chat_session is not None})"
        )