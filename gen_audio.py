#!/usr/bin/env python3
"""Generate all audio clips for a lesson from its spec.json (Piper lessac, local)."""
import json, os, subprocess, sys

V = os.path.expanduser("~/workspace/tools/tts-venv/bin/piper")
M = os.path.expanduser("~/workspace/tools/piper-voices/en_US-lessac-medium.onnx")

def main():
    lesson_dir = os.path.abspath(sys.argv[1])
    spec = json.load(open(os.path.join(lesson_dir, "spec.json"), encoding="utf-8"))
    out = os.path.join(lesson_dir, "audio")
    os.makedirs(out, exist_ok=True)
    for i, text in enumerate(spec["audio_texts"]):
        wav = os.path.join(out, "a%02d.wav" % i)
        mp3 = os.path.join(out, "a%02d.mp3" % i)
        subprocess.run([V, "-m", M, "-f", wav, "--length-scale", "1.35"],
                       input=text.encode(), check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-ac", "1", "-b:a", "48k", mp3], check=True)
        os.remove(wav)
        print("ok a%02d" % i, text)
    print("clips:", len(spec["audio_texts"]))

if __name__ == "__main__":
    main()
