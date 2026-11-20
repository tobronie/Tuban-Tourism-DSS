#!/usr/bin/env python3
"""words.json -> captions.json (a first draft Claude then edits for emphasis/headlines).

  build_captions.py words.json -o captions.json --preset pop [--max-words 3] [--emph "cuan,AI,gratis"]
  build_captions.py words.json --preset editorial --sub subtitle   # headline + running subtitle

Chunking: a new caption starts after sentence punctuation, after a pause > --gap
seconds, or when --max-words is reached. Numbers, money and words in --emph are
marked "emph": true automatically.
"""
import argparse
import json
import re
from pathlib import Path

NUM = re.compile(r"(\d|[$€£¥%]|^rp\.?$|juta|miliar|ribu|ratus)", re.I)


def chunk(words, max_words, gap, hold):
    segs, cur = [], []
    for i, w in enumerate(words):
        if cur:
            prev = cur[-1]
            pause = w["s"] - prev["e"]
            if len(cur) >= max_words or pause > gap or re.search(r"[.!?]$", prev["w"]):
                segs.append(cur)
                cur = []
        cur.append(w)
        if re.search(r"[,;:]$", w["w"]) and len(cur) >= 2:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    out = []
    for k, ws in enumerate(segs):
        nxt = segs[k + 1][0]["s"] if k + 1 < len(segs) else ws[-1]["e"] + hold
        end = min(ws[-1]["e"] + hold, max(ws[-1]["e"], nxt - 0.02))
        out.append({"start": round(ws[0]["s"], 3), "end": round(end, 3), "words": ws})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words")
    ap.add_argument("-o", "--out")
    ap.add_argument("--preset", default="pop")
    ap.add_argument("--max-words", type=int, default=None, help="default depends on preset")
    ap.add_argument("--gap", type=float, default=0.45, help="pause (s) that starts a new caption")
    ap.add_argument("--hold", type=float, default=0.3, help="seconds a caption lingers after its last word")
    ap.add_argument("--emph", default="", help="comma separated words to emphasise")
    ap.add_argument("--sub", default=None, help="also add a running subtitle track with this preset")
    a = ap.parse_args()

    words = json.loads(Path(a.words).read_text())
    emph = {e.strip().lower() for e in a.emph.split(",") if e.strip()}
    for w in words:
        bare = re.sub(r"[^\w$%€£]", "", w["w"].lower())
        if bare and (bare in emph or NUM.search(bare)):
            w["emph"] = True
    default_max = {"pop": 3, "redbox": 4, "editorial": 4, "impact": 1, "subtitle": 5}.get(a.preset, 3)
    segs = chunk(words, a.max_words or default_max, a.gap, a.hold)
    doc = {"preset": a.preset, "style": {}, "segments": segs}
    if a.sub:
        for s in chunk([dict(w) for w in words], 5, a.gap, a.hold):
            s["preset"] = a.sub
            doc["segments"].append(s)
    out = Path(a.out or Path(a.words).with_name(Path(a.words).name.replace(".words.json", "") + ".captions.json"))
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    print(out)


if __name__ == "__main__":
    main()
