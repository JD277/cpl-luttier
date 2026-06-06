import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json
import sys
import time

class STTEngine:
    """
    Motor de Reconocimiento de Voz en Tiempo Real usando Vosk.
    Combina detección de palabra clave (Wake Word) y transcripción por VAD.
    """
    
    def __init__(self, model_path="vosk-model-small-es-0.42", lang="es", sample_rate=16000, 
                 block_size=8000, keyword="epa", silence_duration=2):
        """
        Inicializa el motor de STT.
        
        Args:
            model_path (str): Ruta al modelo Vosk. Si es None, usa lang.
            lang (str): Código de idioma para el modelo por defecto.
            sample_rate (int): Frecuencia de muestreo del audio.
            block_size (int): Tamaño del bloque de audio.
            keyword (str): Palabra clave para activar la escucha.
            silence_duration (float): Segundos de silencio para finalizar.
        """
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.keyword = keyword.lower()
        self.silence_threshold = int(silence_duration * (sample_rate / block_size))
        
        # Cola para datos de audio
        self.audio_queue = queue.Queue()
        
        # Inicializar modelo Vosk
        try:
            if model_path:
                self.model = Model(model_path)
            else:
                self.model = Model(lang=lang)
            print(f"✅ Modelo Vosk cargado correctamente")
        except Exception as e:
            raise Exception(f"❌ Error al cargar el modelo Vosk: {e}")
        
        # Estado del sistema
        self.is_listening = False

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback interno para capturar audio desde el micrófono."""
        if status:
            print(f"⚠️ Audio Status: {status}", file=sys.stderr)
        self.audio_queue.put(bytes(indata))

    def _create_stream(self):
        """Crea y retorna un stream de audio configurado."""
        return sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            dtype='int16',
            channels=1,
            callback=self._audio_callback
        )

    def wait_for_keyword(self):
        """
        Bloquea la ejecución hasta detectar la palabra clave.
        
        Returns:
            bool: True si se detectó la keyword, False si hubo error.
        """
        recognizer = KaldiRecognizer(self.model, self.sample_rate)
        #print(f"🎤 Esperando palabra clave: '{self.keyword}'...")
        
        try:
            with self._create_stream():
                while self.is_listening or not self.audio_queue.empty():
                    try:
                        data = self.audio_queue.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())['text']
                        if self.keyword in result:
                            print(f"✅ Keyword detectada: '{self.keyword}'")
                            return True
                    else:
                        partial = json.loads(recognizer.PartialResult())['partial']
                        print(f"🔍 Escuchando... (parcial: '{partial}')", end='\r') 
                        if self.keyword in partial:
                            print(f"✅ Keyword detectada (parcial): '{self.keyword}'")
                            return True
        except KeyboardInterrupt:
            print("\n🛑 Interrupción durante espera de keyword")
            return False
        except Exception as e:
            print(f"❌ Error en wait_for_keyword: {e}")
            return False

    def transcribe_until_silence(self):
        """
        Transcribe audio hasta detectar un periodo de silencio.
        
        Returns:
            str: Texto transcrito o string vacío.
        """
        recognizer = KaldiRecognizer(self.model, self.sample_rate)
        print("🎙️ Escuchando... (habla ahora)")
        
        silence_counter = 0
        final_text = ""
        
        try:
            with self._create_stream():
                while True:
                    try:
                        data = self.audio_queue.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())['text']
                        if result:
                            silence_counter = 0
                            final_text += f" {result}"
                    else:
                        partial = json.loads(recognizer.PartialResult())['partial']
                        if partial == "":
                            silence_counter += 1
                        else:
                            silence_counter = 0
                    
                    if silence_counter > self.silence_threshold:
                        print("⏸️ Silencio detectado, finalizando...")
                        break
                        
        except KeyboardInterrupt:
            print("\n🛑 Transcripción interrumpida")
            return ""
        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            return ""
        
        # Obtener resultado final pendiente
        final_result = json.loads(recognizer.FinalResult())['text']
        if final_result:
            final_text += f" {final_result}"
            
        return final_text.strip()

    def listen_and_transcribe(self):
        """
        Flujo completo: Espera keyword -> Transcribe -> Retorna texto.
        
        Returns:
            str: Texto transcrito o string vacío.
        """
        self.is_listening = True
        
        try:
            # Paso 1: Detectar keyword
            if not self.wait_for_keyword():
                return ""
            
            # Pausa breve y limpieza de buffer
            time.sleep(0.3)
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Paso 2: Transcribir
            text = self.transcribe_until_silence()
            
            if text:
                print(f"📝 Resultado: '{text}'")
            
            return text
            
        finally:
            self.is_listening = False

    def stop(self):
        """Detiene cualquier operación de escucha activa."""
        self.is_listening = False
        print("🛑 Motor STT detenido")


# ==================== EJEMPLO DE USO ====================
if __name__ == "__main__":
    # Inicializar el motor
    stt = STTEngine(
        keyword="epa",
        silence_duration=1.5,
        # model_path="models/vosk-model-small-es-0.42"  # Descomentar si usas ruta local
    )
    
    print("=" * 50)
    print("Sistema STT POO listo")
    print("=" * 50)
    
    try:
        while True:
            texto = stt.listen_and_transcribe()
            
            if texto:
                # Aquí integras con tu lógica de negocio
                print(f"🔧 Procesando comando: {texto}")
                # ejemplo: enviar_a_firestore(texto)
                # ejemplo: enviar_comando_serial(texto)
            
            continuar = input("\n¿Escuchar de nuevo? (s/n): ").lower()
            if continuar != 's':
                break
                
    except KeyboardInterrupt:
        print("\n👋 Programa finalizado por usuario")
    finally:
        stt.stop()

