from __future__ import annotations

import sys
import traceback

from .audio_io import listen_once, transcribe, tts_kokoro, play_wav


def _call_agent_once(user_text: str) -> str:
    """
    Tries a few common crew entrypoints:
      1) hw1_digital_twin_lite_joanna.crew.run_once(user_text)
      2) hw1_digital_twin_lite_joanna.main.run_once / run / kickoff / main(user_text)
      3) hw1_digital_twin_lite_joanna.crew.Hw1DigitalTwinLiteJoannaCrew().crew().kickoff(...)
    If none exist, raises with a clear instruction.
    """
    try:
        from .crew import run_once  # type: ignore
        return str(run_once(user_text))
    except Exception:
        pass
    try:
        from . import main as _m  # type: ignore
        for fn_name in ("run_once", "run", "kickoff", "main"):
            fn = getattr(_m, fn_name, None)
            if callable(fn):
                return str(fn(user_text))
    except Exception:
        pass
    try:
        from .crew import Hw1DigitalTwinLiteJoannaCrew  # type: ignore
        inst = Hw1DigitalTwinLiteJoannaCrew()
        crew = inst.crew()
        result = crew.kickoff(
            inputs={
                "prompt": user_text,
                "user_text": user_text,
                "query": user_text,
                "input": user_text,
                "topic": user_text,
            }
        )
        return str(result)
    except Exception:
        pass
    raise RuntimeError(
        "Could not find a callable crew entrypoint. "
        "Add `run_once(user_text: str) -> str` to crew.py."
    )


def main() -> None:
    print("🎙️  Speak; pause to end your utterance. Ctrl+C to exit.")
    try:
        while True:
            wav_in = listen_once()
            user_text = transcribe(wav_in)
            if not user_text:
                print("(heard silence)")
                continue
            print(f"You: {user_text}")
            try:
                reply = _call_agent_once(user_text).strip()
            except Exception:
                print("Agent error — see traceback below and wire `run_once` as noted.")
                traceback.print_exc()
                reply = "Sorry, I couldn't reach the agent yet. Please wire `run_once` in crew.py."
            print(f"Agent: {reply}")
            wav_out = tts_kokoro(reply)
            play_wav(wav_out)
    except KeyboardInterrupt:
        print("\nbye!")


if __name__ == "__main__":
    main()
