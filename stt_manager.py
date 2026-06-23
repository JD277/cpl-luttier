import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json
import sys
import time

class STTEngine:
    """Motor STT con Vosk. Crea reconocedores frescos para cada tarea."""
    
    def __init__(self, model_path="vosk-model-small-es-0.42", sample_rate=16000, 
                block_size=8000, silence_duration=2.0):
        self.sample_rate = sample_rate
        self.block_size = block_size
        # ✅ Guardamos los segundos reales para usar con time.time()
        self.silence_duration = float(silence_duration) 
        
        try:
            self.model = Model(model_path)
            print(f"✅ Modelo Vosk cargado: {model_path}")
        except Exception as e:
            raise RuntimeError(f" Error cargando modelo Vosk: {e}")
        
    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"⚠️ Audio Status: {status}", file=sys.stderr)
        self.audio_queue.put(bytes(indata))

    def _create_stream(self):
        return sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            dtype='int16',
            channels=1,
            callback=self._audio_callback
        )

    def wait_for_keyword(self, word):
        """Bloquea hasta detectar la palabra clave. Reconocedor NUEVO."""
        self.audio_queue = queue.Queue()
        # IMPORTANTE: Nuevo reconocedor para esta tarea específica
        rec = KaldiRecognizer(self.model, self.sample_rate)
        
        print(f"🎤 Esperando keyword: '{word}'...")
        
        try:
            with self._create_stream():
                while True:
                    try:
                        data = self.audio_queue.get(timeout=1.0)
                    except queue.Empty:
                        continue
                    
                    # AcceptWaveform devuelve True cuando hay una frase completa
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())['text']
                        #print(f"   📝 Resultado completo: '{result}'")
                        if result and word.lower() in result.lower():
                            print(f"✅ Keyword detectada: '{word}'")
                            return True
                    else:
                        # PartialResult da feedback en tiempo real sin cerrar frase
                        partial = json.loads(rec.PartialResult())['partial']
                        #print(f"   📝 Resultado parcial: '{partial}'")
                        if partial and word.lower() in partial.lower():
                            print(f"✅ Keyword detectada (parcial): '{word}'")
                            return True
                            
        except KeyboardInterrupt:
            print("\n🛑 Interrupción en espera de keyword")
            return False
        except Exception as e:
            print(f"❌ Error en wait_for_keyword: {e}")
            return False

    def transcribe_until_silence(self):
        """Transcribe hasta detectar silencio real medido por tiempo."""
        self.audio_queue = queue.Queue()
        rec = KaldiRecognizer(self.model, self.sample_rate)
        
        print("🎙️ Escuchando... (di 'Terminar' para salir)")
        
        last_activity_time = time.time()  # Marca inicial de actividad
        final_text = ""
        
        try:
            with self._create_stream():
                while True:
                    try:
                        data = self.audio_queue.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    
                    current_time = time.time()
                    has_activity = False
                    
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())['text']
                        if result:
                            has_activity = True
                            final_text += f" {result}"
                            print(f"   📝 Detectado: '{result}'")
                    else:
                        partial = json.loads(rec.PartialResult())['partial']
                        if partial:
                            has_activity = True
                    
                    # Actualizar marca de tiempo solo si hubo actividad real
                    if has_activity:
                        last_activity_time = current_time
                    
                    # Calcular silencio REAL acumulado
                    silence_elapsed = current_time - last_activity_time
                    if silence_elapsed >= self.silence_duration:
                        print(f"⏸️ Silencio de {silence_elapsed:.1f}s detectado.")
                        break
                        
        except KeyboardInterrupt:
            print("\n🛑 Transcripción interrumpida")
            return ""
        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            return ""
        
        final_result = json.loads(rec.FinalResult())['text']
        if final_result:
            final_text += f" {final_result}"
            
        return final_text.strip()