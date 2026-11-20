#!/usr/bin/env python3
"""Word-level transcription -> words.json  ([{"w": "kata", "s": 0.42, "e": 0.71}, ...])

  transcribe.py VIDEO [-o words.json] [--lang id] [--model small]
  transcribe.py VIDEO --srt subs.srt        # no ASR: spread SRT cue words evenly over each cue

Uses faster-whisper (pip install faster-whisper). The model is downloaded from
Hugging Face on first use. Bigger model = better Indonesian accuracy but slower:
tiny < base < small (default) < medium < large-v3.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def from_srt(path):
    txt = Path(path).read_text(encoding="utf-8-sig")
    words = []
    ts = lambda h, m, s, ms: int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    for block in re.split(r"\n\s*\n", txt.strip()):
        lines = block.strip().splitlines()
        for i, line in enumerate(lines):
            m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", line)
            if m:
                a, b = ts(*m.groups()[:4]), ts(*m.groups()[4:])
                toks = " ".join(lines[i + 1:]).split()
                if not toks:
                    break
                # weight duration by word length so long words get more time
                tot = sum(len(t) + 2 for t in toks)
                t = a
                for tok in toks:
                    d = (b - a) * (len(tok) + 2) / tot
                    words.append({"w": tok, "s": round(t, 3), "e": round(t + d, 3)})
                    t += d
                break
    return words


def asr(video, model_name, lang, device):
    from faster_whisper import WhisperModel
    compute = "int8" if device == "cpu" else "float16"
    model = WhisperModel(model_name, device=device, compute_type=compute)
    segs, info = model.transcribe(video, language=lang, word_timestamps=True, vad_filter=True,
                                  beam_size=5, condition_on_previous_text=False)
    print(f"[asr] language={info.language} p={info.language_probability:.2f} dur={info.duration:.1f}s",
          file=sys.stderr)
    words = []
    for seg in segs:
        for w in seg.words or []:
            tok = w.word.strip()
            if tok:
                words.append({"w": tok, "s": round(w.start, 3), "e": round(w.end, 3)})
        print(f"  [{seg.start:6.2f}-{seg.end:6.2f}] {seg.text.strip()}", file=sys.stderr)
    return words


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("-o", "--out")
    ap.add_argument("--lang", default="id", help="language code, or 'auto' (default: id)")
    ap.add_argument("--model", default="small")
    ap.add_argument("--device", default="auto", help="cpu | cuda | auto")
    ap.add_argument("--srt", help="use an existing SRT instead of ASR")
    a = ap.parse_args()
    out = Path(a.out or (str(Path(a.video).with_suffix("")) + ".words.json"))
    if a.srt:
        words = from_srt(a.srt)
    else:
        device = a.device
        if device == "auto":
            try:
                import ctranslate2
                device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
            except Exception:
                device = "cpu"
        words = asr(a.video, a.model, None if a.lang == "auto" else a.lang, device)
    out.write_text(json.dumps(words, ensure_ascii=False, indent=0))
    print(f"[ok] {len(words)} words -> {out}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
