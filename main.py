import os
import time
from stt_manager import STTEngine
from gemini import GeminiManager
from tts import speak

# Configuración
API_KEY = "AIzaSyCUJ43mng-KzhWzmBT8S_DfzF2U9FyTGOs"
MAX_EMPTY_ATTEMPTS = 3
GRACE_PERIOD = 5.0

# ✅ MODELO GEMMA OFICIAL DE LA API (según tu especificación)
gemini = GeminiManager(
    model_name="gemma-4-31b-it",
    api_key=API_KEY,
    system_instruction=(
        "Eres Lutier, luthier experto en cuatros venezolanos. "
        "Responde SIEMPRE en español, máximo una oración corta. "
        "PROHIBIDO mostrar razonamiento, viñetas o notas internas."
    ),
    temperature=0.5
)

vosk = STTEngine()

MODE_INSTRUCTIONS = {
    "mod": "Modo Modificación: Espera instrucción específica del usuario para aplicar cambios al cuatro.",
    "revision": "Modo Revisión: Realiza diagnóstico automático del instrumento.",
    "conversacion": "Modo Conversación: Interactúa naturalmente como asistente luthier."
}

def announce_mode(mode: str):
    msg = f"Entrando al modo {mode}"
    print(f"🔊 {msg}")
    # ✅ Pausa crítica: libera recursos de red/STT antes de hablar
    time.sleep(0.3)
    speak(msg)

def get_mode(text: str) -> str | None:
    if not text: 
        return None
    t = text.lower()
    if any(k in t for k in ["mod", "modificar", "ajuste"]): 
        return "mod"
    if any(k in t for k in ["revision", "revisión", "revisar", "evaluar", "diagnóstico"]): 
        return "revision"
    if any(k in t for k in ["conversa", "hablar", "charlar"]): 
        return "conversacion"
    return None

def safe_speak(text: str):
    """Wrapper seguro que garantiza pausa previa para pyttsx3."""
    if not text or not text.strip():
        return
    time.sleep(0.3)  # ✅ Libera bloqueo de red y buffer de audio
    speak(text)

def handle_mod_mode():
    """Bloqueo síncrono: espera UNA sola instrucción válida."""
    print("️ Modo MOD: Esperando instrucción única...")
    
    while True:
        text = vosk.transcribe_until_silence()
        
        if not text:
            continue
            
        if "cancelar" in text.lower() or "salir" in text.lower():
            print("↩️ Modo Mod cancelado por usuario")
            safe_speak("Modo modificación cancelado")
            return None
            
        print(f"👤 Instrucción Mod: {text}")
        
        response_obj = gemini.send_message(f"{MODE_INSTRUCTIONS['mod']}\nUsuario: {text}")
        
        if hasattr(response_obj, 'text'):
            response_text = response_obj.text
        else:
            response_text = str(response_obj)
            
        clean = response_text.strip()
        print(f"🤖 Lutier: {clean}")
        
        safe_speak(clean)
        return "completed"

def handle_revision_mode():
    """Acción automática única al entrar."""
    print("🔍 Modo REVISIÓN: Iniciando diagnóstico automático...")
    
    # TODO: Integrar captura ESP32-CAM + Gemini Vision aquí
    response = "Diagnóstico completado: El cuatro presenta tensión adecuada en las cuerdas."
    print(f"🤖 Lutier: {response}")
    
    # ✅ safe_speak garantiza que pyttsx3 tenga tiempo de inicializar
    safe_speak(response)
    
    return "completed"

def handle_conversation_mode():
    """Bucle persistente con contador de silencios y ventana de gracia."""
    print("💬 Modo CONVERSACIÓN activo. Di 'terminar' para salir.")
    empty_count = 0
    
    while empty_count < MAX_EMPTY_ATTEMPTS:
        text = vosk.transcribe_until_silence()
        
        if text and "terminar" in text.lower():
            print("🛑 Sesión terminada")
            safe_speak("Sesión finalizada")
            gemini.clear_chat()
            return "exit"
            
        if text:
            new_mode = get_mode(text)
            if new_mode and new_mode != "conversacion":
                return new_mode
            
            print(f"👤 Usuario: {text}")
            empty_count = 0
            response = gemini.send_message(f"{MODE_INSTRUCTIONS['conversacion']}\nUsuario: {text}")
            
            if hasattr(response, 'text'):
                response_text = response.text
            else:
                response_text = str(response)
                
            clean = response_text.strip()
            print(f"🤖 Lutier: {clean}")
            safe_speak(clean)
        
        else:
            empty_count += 1
            if empty_count >= MAX_EMPTY_ATTEMPTS:
                print(f"⏳ Pausa prolongada. Tienes {GRACE_PERIOD}s extra...")
                grace_start = time.time()
                recovered = False
                
                while time.time() - grace_start < GRACE_PERIOD:
                    text_grace = vosk.transcribe_until_silence()
                    if text_grace:
                        print("✅ Voz detectada en ventana de gracia")
                        empty_count = 0
                        recovered = True
                        break
                    remaining = GRACE_PERIOD - (time.time() - grace_start)
                    print(f"   ⏱️ Quedan {remaining:.1f}s...", end='\r')
                
                if not recovered:
                    print("\n💤 Modo conversación desactivado por inactividad")
                    safe_speak("Modo conversación desactivado")
                    gemini.clear_chat()
                    return "inactive"
            else:
                remaining = MAX_EMPTY_ATTEMPTS - empty_count
                print(f"⚠️ Sin audio ({remaining} intentos restantes)")

# === BUCLE PRINCIPAL ===
print("🎙️ Sistema listo. Di 'Luthier' para activar.")

while True:
    # ✅ KEYWORD EXACTA SEGÚN TU ESPECIFICACIÓN
    if vosk.wait_for_keyword("Luthier"):
        print("✅ Keyword detectada. Esperando modo...")
        mode_text = vosk.transcribe_until_silence()
        current_mode = get_mode(mode_text) if mode_text else None
        
        if not current_mode:
            print("️ Modo no reconocido")
            safe_speak("Di Mod, Revisión o Conversación")
            continue
        
        announce_mode(current_mode.upper())
        gemini.start_chat()
        
        result = None
        if current_mode == "mod":
            result = handle_mod_mode()
        elif current_mode == "revision":
            result = handle_revision_mode()
        elif current_mode == "conversacion":
            result = handle_conversation_mode()
        
        if result and result in MODE_INSTRUCTIONS:
            current_mode = result
            announce_mode(current_mode.upper())
            gemini.start_chat()
            if current_mode == "mod": 
                handle_mod_mode()
            elif current_mode == "revision": 
                handle_revision_mode()
            elif current_mode == "conversacion": 
                handle_conversation_mode()
        
        # ✅ PAUSA PARA LIMPIAR BUFFER DE AUDIO ANTES DE VOLVER A ESCUCHAR
        time.sleep(0.5)
        print("🔄 Volviendo a espera de keyword 'Luthier'...")