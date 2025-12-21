"""
VAD Test Script - Testa detecção de voz com ruído de fundo (TV)
Compara RMS puro vs WebRTC VAD para validar redução de falsos positivos
"""
import asyncio
import audioop
import os
import wave
from typing import Tuple

# Tenta importar webrtcvad
try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    print("⚠️ webrtcvad não instalado. Execute: pip install webrtcvad")


def load_test_audio(filepath: str) -> bytes:
    """
    Carrega arquivo WAV de teste.
    Deve ser PCM 16-bit, mono, 16kHz.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    
    with wave.open(filepath, 'rb') as wav:
        # Valida formato
        if wav.getnchannels() != 1:
            raise ValueError("Áudio deve ser mono")
        if wav.getsampwidth() != 2:
            raise ValueError("Áudio deve ser 16-bit")
        if wav.getframerate() != 16000:
            raise ValueError("Áudio deve ser 16kHz")
        
        return wav.readframes(wav.getnframes())


def count_speech_frames_rms(audio_data: bytes, threshold: int = 400, frame_duration_ms: int = 30) -> Tuple[int, int]:
    """
    Conta frames detectados como fala usando apenas RMS.
    
    Returns:
        (frames_detectados, total_frames)
    """
    sample_rate = 16000
    frame_size = int(sample_rate * frame_duration_ms / 1000) * 2  # 2 bytes por sample
    
    total_frames = 0
    speech_frames = 0
    
    for i in range(0, len(audio_data), frame_size):
        frame = audio_data[i:i + frame_size]
        if len(frame) < frame_size:
            continue
        
        total_frames += 1
        
        try:
            rms = audioop.rms(frame, 2)
            if rms > threshold:
                speech_frames += 1
        except Exception:
            pass
    
    return speech_frames, total_frames


def count_speech_frames_vad(audio_data: bytes, vad, frame_duration_ms: int = 30) -> Tuple[int, int]:
    """
    Conta frames detectados como fala usando WebRTC VAD.
    
    Returns:
        (frames_detectados, total_frames)
    """
    sample_rate = 16000
    frame_size = int(sample_rate * frame_duration_ms / 1000) * 2
    
    total_frames = 0
    speech_frames = 0
    
    for i in range(0, len(audio_data), frame_size):
        frame = audio_data[i:i + frame_size]
        if len(frame) != frame_size:
            continue
        
        total_frames += 1
        
        try:
            if vad.is_speech(frame, sample_rate):
                speech_frames += 1
        except Exception:
            pass
    
    return speech_frames, total_frames


def count_speech_frames_dual(audio_data: bytes, vad, rms_threshold: int = 400, frame_duration_ms: int = 30) -> Tuple[int, int, int]:
    """
    Conta frames usando validação dupla (RMS + VAD).
    
    Returns:
        (frames_rms_only, frames_vad_confirmed, total_frames)
    """
    sample_rate = 16000
    frame_size = int(sample_rate * frame_duration_ms / 1000) * 2
    
    total_frames = 0
    rms_detections = 0
    vad_confirmed = 0
    
    for i in range(0, len(audio_data), frame_size):
        frame = audio_data[i:i + frame_size]
        if len(frame) != frame_size:
            continue
        
        total_frames += 1
        
        try:
            rms = audioop.rms(frame, 2)
            if rms > rms_threshold:
                rms_detections += 1
                
                # Segunda validação com VAD
                if vad.is_speech(frame, sample_rate):
                    vad_confirmed += 1
        except Exception:
            pass
    
    return rms_detections, vad_confirmed, total_frames


async def test_vad_with_tv_noise():
    """Testa VAD com ruído de TV"""
    if not WEBRTCVAD_AVAILABLE:
        print("❌ webrtcvad não disponível")
        return
    
    print("\n" + "=" * 60)
    print("🎤 TESTE DE VAD - RUÍDO DE FUNDO (TV)")
    print("=" * 60)
    
    # Inicializa VAD com agressividade 2 (balanceado)
    vad = webrtcvad.Vad(2)
    
    # Define arquivos de teste
    test_files = [
        ("tests/audio/tv_background.wav", "TV ligada + pessoa falando"),
        ("tests/audio/clean_speech.wav", "Fala limpa (sem ruído)"),
        ("tests/audio/only_tv.wav", "Apenas TV (sem fala)"),
    ]
    
    for filepath, description in test_files:
        print(f"\n📂 Testando: {description}")
        print(f"   Arquivo: {filepath}")
        
        try:
            audio_data = load_test_audio(filepath)
            
            # RMS puro
            rms_speech, rms_total = count_speech_frames_rms(audio_data, threshold=400)
            rms_ratio = rms_speech / max(rms_total, 1) * 100
            
            # VAD puro
            vad_speech, vad_total = count_speech_frames_vad(audio_data, vad)
            vad_ratio = vad_speech / max(vad_total, 1) * 100
            
            # Dupla validação
            dual_rms, dual_vad, dual_total = count_speech_frames_dual(audio_data, vad, 400)
            false_positives = dual_rms - dual_vad
            
            print(f"\n   📊 RESULTADOS:")
            print(f"   ├── RMS puro:     {rms_speech:4d}/{rms_total} frames ({rms_ratio:.1f}%)")
            print(f"   ├── VAD puro:     {vad_speech:4d}/{vad_total} frames ({vad_ratio:.1f}%)")
            print(f"   ├── Dupla valid.: {dual_vad:4d}/{dual_total} frames")
            print(f"   └── Falsos +:     {false_positives:4d} frames EVITADOS pelo VAD")
            
            # Avaliação
            if false_positives > dual_total * 0.2:
                print(f"   ⚠️  ATENÇÃO: Muitos falsos positivos detectados!")
            else:
                print(f"   ✅ VAD funcionando corretamente")
                
        except FileNotFoundError:
            print(f"   ⚠️  Arquivo não encontrado - pulando teste")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 60)


def test_vad_aggressiveness():
    """Testa diferentes níveis de agressividade do VAD"""
    if not WEBRTCVAD_AVAILABLE:
        print("❌ webrtcvad não disponível")
        return
    
    print("\n" + "=" * 60)
    print("🎚️  TESTE DE AGRESSIVIDADE DO VAD")
    print("=" * 60)
    
    test_file = "tests/audio/tv_background.wav"
    
    try:
        audio_data = load_test_audio(test_file)
    except FileNotFoundError:
        print(f"⚠️ Arquivo de teste não encontrado: {test_file}")
        print("   Crie a pasta tests/audio/ e adicione arquivos WAV de teste")
        return
    
    print(f"\n📂 Arquivo: {test_file}")
    print("\nAgressividade | Frames Detectados | % do Total")
    print("-" * 50)
    
    for aggressiveness in range(4):
        vad = webrtcvad.Vad(aggressiveness)
        speech_frames, total_frames = count_speech_frames_vad(audio_data, vad)
        ratio = speech_frames / max(total_frames, 1) * 100
        
        print(f"     {aggressiveness}        |       {speech_frames:4d}        |   {ratio:5.1f}%")
    
    print("-" * 50)
    print("Nota: Maior agressividade = menos falsos positivos")


def create_test_audio_directory():
    """Cria estrutura de diretórios para testes"""
    os.makedirs("tests/audio", exist_ok=True)
    
    readme_path = "tests/audio/README.md"
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write("""# Arquivos de Áudio para Teste VAD

Adicione os seguintes arquivos WAV (PCM 16-bit, mono, 16kHz):

1. `tv_background.wav` - Pessoa falando com TV ligada ao fundo
2. `clean_speech.wav` - Fala limpa sem ruído de fundo  
3. `only_tv.wav` - Apenas ruído de TV (sem fala humana)

## Como gerar arquivos de teste:

```bash
# Converter para formato correto
ffmpeg -i input.wav -ar 16000 -ac 1 -acodec pcm_s16le output.wav
```
""")
    
    print("✅ Diretório tests/audio/ criado")
    print("   Adicione arquivos WAV de teste conforme README.md")


if __name__ == "__main__":
    # Cria estrutura de testes se não existir
    create_test_audio_directory()
    
    # Executa testes
    print("\n🚀 Iniciando testes de VAD...")
    
    asyncio.run(test_vad_with_tv_noise())
    test_vad_aggressiveness()
