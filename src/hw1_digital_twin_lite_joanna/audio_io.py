import os
import tempfile
import wave
from typing import Optional

import numpy as np
import sounddevice as sd
import webrtcvad
import soundfile as sf

# STT (fast Whisper)
try:
    from faster_whisper import WhisperModel  # type: ignore
except Exception:
    WhisperModel = None

# ✅ Correct Kokoro import: use KPipeline (object you call) — not a module
# Docs/README show: from kokoro import KPipeline; pipeline = KPipeline(...); generator = pipeline(text, voice=..., speed=...)
try:
    from kokoro import KPipeline  # type: ignore
except Exception:
    KPipeline = None

SAMPLE_RATE = 16000   # for VAD-friendly mic capture
CHANNELS = 1
FRAME_MS = 20         # valid: 10/20/30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000

_whisper_model = None
_kokoro_pipeline = None  # cached KPipeline


def _bytes_to_wav(frames: bytes, out_path: Optional[str] = None) -> str:
    if out_path is None:
        out_path = tempfile.mktemp(suffix=".wav")
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # int16
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(frames)
    return out_path


def listen_once(max_secs: int = 15, vad_level: int = 2) -> str:
    """
    Record from the default mic until brief trailing silence.
    Returns a path to a 16kHz mono WAV file.
    """
    vad = webrtcvad.Vad(vad_level)  # 0..3 (3 is most aggressive)
    buf = bytearray()
    voiced_run = 0
    silence_run = 0
    start_trigger = 6         # ~120ms voiced
    stop_trigger = 25         # ~500ms silence
    max_frames = int(max_secs * 1000 / FRAME_MS)

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=FRAME_SAMPLES,
    ) as stream:
        # warm-up
        sd.sleep(120)
        frames_seen = 0
        started = False
        while frames_seen < max_frames:
            data, _ = stream.read(FRAME_SAMPLES)
            frame = bytes(data)
            frames_seen += 1
            is_speech = vad.is_speech(frame, SAMPLE_RATE)
            if is_speech:
                voiced_run += 1
                silence_run = 0
            else:
                silence_run += 1

            if not started and voiced_run >= start_trigger:
                started = True

            if started:
                buf.extend(frame)
                if silence_run >= stop_trigger:
                    break

    return _bytes_to_wav(bytes(buf))


def _load_whisper(model_size: str = "base"):
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    if WhisperModel is None:
        raise RuntimeError("faster-whisper is not installed. Install the 'voice' extra.")
    _whisper_model = WhisperModel(
        model_size,
        device=os.getenv("WHISPER_DEVICE", "cpu"),
        compute_type=os.getenv("WHISPER_COMPUTE", "int8"),
    )
    return _whisper_model


def transcribe(wav_path: str, model_size: str = "base") -> str:
    """
    ASR via faster-whisper. Returns a plain text transcript.
    """
    model = _load_whisper(model_size)
    segments, _info = model.transcribe(
        wav_path,
        beam_size=1,
        language=os.getenv("ASR_LANG") or None,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=300),
        condition_on_previous_text=False,
    )
    text = " ".join(seg.text for seg in segments).strip()
    return text


def _get_kokoro_pipeline(lang_code: str):
    """
    Build or reuse a Kokoro KPipeline for the given language code.
    Examples: 'a' -> American English, 'b' -> British English, 'f' -> French, 'j' -> Japanese, 'z' -> Mandarin, etc.
    """
    global _kokoro_pipeline
    if _kokoro_pipeline is not None:
        return _kokoro_pipeline
    if KPipeline is None:
        raise RuntimeError("kokoro is not installed. Install the 'voice' extra (includes kokoro-tts which pulls in kokoro).")
    _kokoro_pipeline = KPipeline(lang_code=lang_code)
    return _kokoro_pipeline


def tts_kokoro(text: str, voice: Optional[str] = None, speed: float = 1.0) -> str:
    """
    Synthesize speech with Kokoro and return a WAV path (24kHz).
    Voice hints (English): 'af_sarah', 'am_adam', 'af_bella', 'am_michael', etc.
    """
    if not text:
        text = "..."
    # Default voice & lang code
    voice = voice or os.getenv("KOKORO_VOICE", "af_sarah")
    # Derive lang code from the first letter of the voice unless overwritten
    lang_code = os.getenv("KOKORO_LANG", voice[0].lower() if voice else "a")
    pipeline = _get_kokoro_pipeline(lang_code)

    # Generate audio chunks
    gen = pipeline(text, voice=voice, speed=speed, split_pattern=r"\n+")
    chunks = []
    for _i, (_gs, _ps, audio) in enumerate(gen):
        # audio: float32 PCM at 24kHz
        chunks.append(audio)

    all_audio = np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.float32)
    out_path = tempfile.mktemp(suffix=".wav")
    sf.write(out_path, all_audio, 24000)  # write 24kHz WAV
    return out_path


def play_wav(path: str) -> None:
    import simpleaudio as sa
    with sf.SoundFile(path, "rb") as f:
        data = f.read(dtype="int16")
        play_obj = sa.play_buffer(
            data.tobytes(),
            num_channels=f.channels,
            bytes_per_sample=2,
            sample_rate=f.samplerate,
        )
        play_obj.wait_done()
