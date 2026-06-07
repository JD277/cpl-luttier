# tts.py
import pyttsx3
import threading

class TTSEngine:
    """Motor TTS local seguro para hilos múltiples."""
    
    _instance = None
    _lock = threading.Lock()       # Protege la inicialización singleton
    _speak_lock = threading.Lock() # ✅ Cola de reproducción (evita run loop collision)
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = pyttsx3.init()
                    cls._instance.setProperty('rate', 170)
                    cls._instance.setProperty('volume', 0.9)
                    # Intentar voz mexicana; fallback automático si no existe
                    voices = cls._instance.getProperty('voices')
                    mx_voice = next((v for v in voices if 'MX' in v.id or 'Sabina' in v.name), None)
                    if mx_voice:
                        cls._instance.setProperty('voice', mx_voice.id)
        return cls._instance
    
    @staticmethod
    def speak(text: str):
        """Reproduce texto de forma segura y NO BLOQUEANTE."""
        if not text or not text.strip():
            return
            
        def _safe_speak():
            # ✅ Bloqueo estricto: espera a que termine cualquier audio anterior
            with TTSEngine._speak_lock:
                try:
                    engine = TTSEngine.get_instance()
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print(f"❌ Error TTS: {e}")
        
        t = threading.Thread(target=_safe_speak, daemon=True)
        t.start()

# Alias global compatible con main.py
speak = TTSEngine.speak