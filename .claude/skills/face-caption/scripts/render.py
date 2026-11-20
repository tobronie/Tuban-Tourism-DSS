#!/usr/bin/env python3
"""Render animated word-by-word captions that float above the speaker's face.

Usage:
  render.py VIDEO CAPTIONS.json -o OUT.mp4
  render.py VIDEO CAPTIONS.json --preview 1.2,3.5,7   # PNG stills + contact sheet only

The video is decoded with ffmpeg, the face is tracked (OpenCV Haar cascade,
cached next to the video as <video>.face.json), captions are drawn with Pillow
and composited per frame, then re-encoded with the original audio.
"""
import argparse
import io
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SKILL_DIR = Path(__file__).resolve().parent.parent
FONT_DIR = SKILL_DIR / "fonts"
PRESETS = json.loads((SKILL_DIR / "presets.json").read_text())
CACHE_DIR = Path(os.environ.get("FACE_CAPTION_CACHE", Path.home() / ".cache" / "face-caption"))
SEG_MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/image_segmenter/"
                 "selfie_segmenter/float16/latest/selfie_segmenter.tflite")

DEFAULTS = {
    "font": "Poppins-ExtraBold.ttf", "font_variation": None, "size": 0.08, "case": "none",
    "color": "#FFFFFF", "emph_color": None, "emph_font": None, "emph_scale": 1.0,
    "emph_glow": False, "active_color": None, "box_text_color": None,
    "spoken_box": None, "active_box": None, "emph_box": None,
    "box_pad": [0.28, 0.10], "box_radius": 0.2,
    "upcoming": "hidden", "dim_color": "#FFFFFF", "dim_alpha": 0.4,
    "anim": "pop", "anim_dur": 0.2, "exit_dur": 0.15,
    "shadow": {"blur": 0.01, "dx": 0.0, "dy": 0.005, "alpha": 0.6},
    "stroke": 0.0, "stroke_color": "#000000",
    "kicker_font": "Poppins-SemiBold.ttf", "kicker_size": 0.032, "kicker_color": "#FFFFFF",
    "kicker_tracking": 0.12,
    "max_words_per_line": 3, "max_width": 0.88, "fit_width": False,
    "line_spacing": 1.0, "word_spacing": 0.22,
    "anchor": "above_face", "pos": None, "gap": 0.02, "overlap": 0.0, "head_pad": 0.22,
    "follow": "smooth", "follow_x": 0.8, "margin": 0.04, "safe_top": 0.06, "safe_bottom": 0.12,
    "behind": False, "strip_punct": True, "hold": 0.25,
}


# ----------------------------------------------------------------------------- utils
def log(*a):
    print(*a, file=sys.stderr, flush=True)


def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def ease_out_cubic(p):
    return 1 - (1 - p) ** 3


def ease_out_back(p, c1=1.70158):
    c3 = c1 + 1
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


def hex_rgba(h, alpha=1.0):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    a = int(h[6:8], 16) if len(h) == 8 else 255
    return (r, g, b, int(a * alpha))


def video_info(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,avg_frame_rate,r_frame_rate:format=duration", "-of", "json", path],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)

    def rate(s):
        try:
            n, d = s.split("/")
            return float(n) / float(d) if float(d) else 0.0
        except Exception:
            return 0.0

    vs = [s for s in j["streams"] if s.get("codec_type") == "video"]
    has_audio = any(s.get("codec_type") == "audio" for s in j["streams"])
    fps = rate(vs[0].get("avg_frame_rate", "0/0")) or rate(vs[0].get("r_frame_rate", "0/0")) or 30.0
    if fps > 61:
        fps = 30.0
    dur = float(j["format"]["duration"])
    png = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-frames:v", "1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    W, H = Image.open(io.BytesIO(png)).size  # displayed size (after rotation metadata)
    return W, H, fps, dur, has_audio


def read_exact(stream, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = stream.read(n - len(buf))
        if not chunk:
            break
        buf += chunk
    return bytes(buf)


# ----------------------------------------------------------------------------- face track
def track_faces(path, W, H, dur, rate=6.0, smooth_sec=0.35):
    import cv2
    aw = 360
    ah = int(round(H * aw / W / 2)) * 2
    casc = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={rate},scale={aw}:{ah}",
                             "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    raw = []
    i = 0
    while True:
        buf = read_exact(proc.stdout, aw * ah)
        if len(buf) < aw * ah:
            break
        g = cv2.equalizeHist(np.frombuffer(buf, np.uint8).reshape(ah, aw))
        faces = casc.detectMultiScale(g, scaleFactor=1.1, minNeighbors=5,
                                      minSize=(int(aw * 0.08), int(aw * 0.08)))
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            raw.append([i / rate, (x + w / 2) / aw, y / ah, (y + h) / ah, w / aw])
        else:
            raw.append([i / rate, None, None, None, None])
        i += 1
    proc.wait()
    n = len(raw)
    found = sum(1 for r in raw if r[1] is not None)
    log(f"[face] {found}/{n} sampled frames have a face")
    t = np.array([r[0] for r in raw]) if n else np.array([0.0])
    cols = []
    default = [0.5, 0.30, 0.45, 0.30]
    for k in range(4):
        v = np.array([np.nan if r[k + 1] is None else r[k + 1] for r in raw]) if n else np.array([np.nan])
        # robust median filter (window 5) kills isolated false positives
        med = v.copy()
        for j in range(len(v)):
            win = v[max(0, j - 2): j + 3]
            win = win[~np.isnan(win)]
            med[j] = np.median(win) if len(win) >= 2 else np.nan
        ok = ~np.isnan(med)
        if ok.sum() == 0:
            med[:] = default[k]
        else:
            med = np.interp(t, t[ok], med[ok])
        cols.append(med)
    cols = np.stack(cols, 1)
    # split on hard cuts so smoothing does not slide text across a cut
    pieces, start = [], 0
    for j in range(1, len(t)):
        dx = abs(cols[j, 0] - cols[j - 1, 0])
        dw = max(cols[j, 3], cols[j - 1, 3]) / max(1e-3, min(cols[j, 3], cols[j - 1, 3]))
        if dx > 0.12 or dw > 1.5:
            pieces.append((start, j))
            start = j
    pieces.append((start, len(t)))
    sigma = max(0.5, smooth_sec * rate)
    rad = int(3 * sigma)
    kern = np.exp(-0.5 * (np.arange(-rad, rad + 1) / sigma) ** 2)
    out = cols.copy()
    for a, b in pieces:
        seg = cols[a:b]
        pad = np.pad(seg, ((rad, rad), (0, 0)), mode="edge")
        for k in range(4):
            out[a:b, k] = np.convolve(pad[:, k], kern / kern.sum(), mode="valid")
    return {"rate": rate, "t": t.tolist(), "cx": out[:, 0].tolist(), "top": out[:, 1].tolist(),
            "bottom": out[:, 2].tolist(), "w": out[:, 3].tolist(), "cuts": [t[a] for a, _ in pieces[1:]]}


class Face:
    def __init__(self, track):
        self.tr = track
        self.t = np.array(track["t"])

    def at(self, t):
        g = lambda k: float(np.interp(t, self.t, np.array(self.tr[k])))
        return {"cx": g("cx"), "top": g("top"), "bottom": g("bottom"), "w": g("w")}


# ----------------------------------------------------------------------------- segmentation (behind-head)
class Segmenter:
    def __init__(self):
        from mediapipe.tasks.python import vision
        from mediapipe.tasks.python.core import base_options
        import mediapipe as mp
        self.mp = mp
        model = CACHE_DIR / "selfie_segmenter.tflite"
        if not model.exists():
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            log("[behind] downloading selfie segmenter model ...")
            urllib.request.urlretrieve(SEG_MODEL_URL, model)
        opts = vision.ImageSegmenterOptions(
            base_options=base_options.BaseOptions(model_asset_path=str(model)),
            output_confidence_masks=True, output_category_mask=False)
        self.seg = vision.ImageSegmenter.create_from_options(opts)

    def close(self):
        try:
            self.seg.close()
        except Exception:
            pass

    def mask(self, frame):  # frame HxWx3 uint8 -> HxW float person prob
        import cv2
        H, W = frame.shape[:2]
        sw = 384
        sh = int(H * sw / W)
        small = np.ascontiguousarray(cv2.resize(frame, (sw, sh), interpolation=cv2.INTER_AREA))
        img = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=small)
        m = self.seg.segment(img).confidence_masks[0].numpy_view().astype(np.float32)
        if m.ndim == 3:
            m = m[..., 0]
        m = cv2.GaussianBlur(m, (0, 0), 1.2)
        m = np.clip((m - 0.35) / 0.3, 0, 1)
        return cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)


# ----------------------------------------------------------------------------- fonts & sprites
_fonts = {}


def font_path(name):
    for p in (Path(name), FONT_DIR / name):
        if p.is_file():
            return str(p)
    try:
        q = subprocess.run(["fc-match", "-f", "%{file}", name], capture_output=True, text=True).stdout
        if q and Path(q).is_file():
            return q
    except FileNotFoundError:
        pass
    log(f"[font] '{name}' not found, falling back to Poppins-ExtraBold")
    return str(FONT_DIR / "Poppins-ExtraBold.ttf")


def get_font(name, px, variation=None):
    key = (name, int(px), variation)
    if key not in _fonts:
        f = ImageFont.truetype(font_path(name), max(6, int(px)))
        if variation:
            try:
                f.set_variation_by_name(variation)
            except Exception as e:  # not a variable font
                log(f"[font] variation '{variation}' ignored: {e}")
        _fonts[key] = f
    return _fonts[key]


def vmetrics(font, upper):
    """(ascent_above_baseline, descent_below_baseline) of a reference glyph set."""
    ref = "HÁ" if upper else "Hg"
    l, t, r, b = font.getbbox(ref, anchor="ls")
    if upper:
        b = max(b, int(font.size * 0.02))
        t = font.getbbox("H", anchor="ls")[1]
    return -t, b


_sprites = {}


def word_sprite(text, font, upper, fill, box=None, pad=(0, 0), radius=0.0, shadow=None,
                glow=None, stroke=0, stroke_fill=None, tracking=0.0):
    """Returns (RGBA image, (ox, oy, cw, ch)) where (ox,oy,cw,ch) is the content box."""
    key = (text, id(font), upper, fill, box, tuple(pad), radius, json.dumps(shadow, sort_keys=True),
           glow, stroke, stroke_fill, tracking)
    if key in _sprites:
        return _sprites[key]
    px = font.size
    asc, desc = vmetrics(font, upper)
    track_px = tracking * px
    if track_px:
        tw = sum(font.getlength(c) + track_px for c in text) - track_px
    else:
        tw = font.getlength(text)
    padx, pady = (pad[0] * px, pad[1] * px) if box else (0, 0)
    cw, ch = int(math.ceil(tw + 2 * padx + 2 * stroke)), int(math.ceil(asc + desc + 2 * pady))
    sb = shadow["blur"] if shadow else 0  # shadow values are already in pixels here
    m = int(math.ceil(max(sb * 3 + abs(shadow["dx"]) + abs(shadow["dy"]) if shadow else 0,
                          px * 0.35 if glow else 0, stroke + 2)))
    Wd, Hd = cw + 2 * m, ch + 2 * m
    layer = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if box:
        d.rounded_rectangle([m, m, m + cw - 1, m + ch - 1], radius=radius * px, fill=hex_rgba(box))
    bx, by = m + padx + stroke, m + pady + asc
    if track_px:
        x = bx
        for c in text:
            d.text((x, by), c, font=font, fill=fill, anchor="ls", stroke_width=stroke, stroke_fill=stroke_fill)
            x += font.getlength(c) + track_px
    else:
        d.text((bx, by), text, font=font, fill=fill, anchor="ls", stroke_width=stroke, stroke_fill=stroke_fill)
    out = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    a = layer.getchannel("A")
    if glow:
        g = Image.new("RGBA", (Wd, Hd), hex_rgba(glow))
        g.putalpha(a.filter(ImageFilter.GaussianBlur(px * 0.18)).point(lambda v: int(v * 0.75)))
        out = Image.alpha_composite(out, g)
    if shadow and shadow.get("alpha", 0) > 0:
        s = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 255))
        sa = a.filter(ImageFilter.GaussianBlur(max(0.1, sb))).point(lambda v: int(v * shadow["alpha"]))
        s.putalpha(sa)
        off = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
        off.paste(s, (int(round(shadow["dx"])), int(round(shadow["dy"]))))
        out = Image.alpha_composite(out, off)
    out = Image.alpha_composite(out, layer)
    res = (out, (m, m, cw, ch))
    _sprites[key] = res
    return res


# ----------------------------------------------------------------------------- captions model
PUNCT_STRIP = re.compile(r"[,.;:]+$")


def style_for(seg, doc):
    st = dict(DEFAULTS)
    name = seg.get("preset") or doc.get("preset") or "pop"
    if name not in PRESETS:
        raise SystemExit(f"unknown preset '{name}'. available: {', '.join(k for k in PRESETS if not k.startswith('_'))}")
    st.update({k: v for k, v in PRESETS[name].items() if not k.startswith("_")})
    if not seg.get("preset") or seg.get("preset") == doc.get("preset"):
        st.update(doc.get("style", {}))
    st.update(seg.get("style", {}))
    return st


def disp_text(w, st):
    s = w.get("text", w.get("w", "")).strip()
    if st["strip_punct"]:
        s = PUNCT_STRIP.sub("", s)
    if st["case"] == "upper":
        s = s.upper()
    elif st["case"] == "lower":
        s = s.lower()
    return s


def layout(seg, st, W, H):
    """Compute word boxes relative to the block's top-left corner (stable for the whole segment)."""
    upper = st["case"] == "upper"
    base_px = st["size"] * W
    words = []
    for w in seg["words"]:
        txt = disp_text(w, st)
        if not txt:
            continue
        emph = bool(w.get("emph"))
        fname = st["emph_font"] if (emph and st["emph_font"]) else st["font"]
        var = None if (emph and st["emph_font"]) else st["font_variation"]
        scale = (st["emph_scale"] if emph else 1.0) * float(w.get("scale", 1.0))
        words.append({"text": txt, "fname": fname, "var": var, "px": base_px * scale, "emph": emph,
                      "s": float(w["s"]), "e": float(w["e"]), "br": bool(w.get("br"))})

    maxw = st["max_width"] * W
    has_box = bool(st["spoken_box"] or st["active_box"] or st["emph_box"])

    def measure(wd, k=1.0):
        f = get_font(wd["fname"], wd["px"] * k, wd["var"])
        asc, desc = vmetrics(f, upper)
        padx, pady = (st["box_pad"][0] * f.size, st["box_pad"][1] * f.size) if has_box else (0, 0)
        return f, f.getlength(wd["text"]) + 2 * padx, asc + pady, desc + pady

    # greedy line breaking
    lines, cur, cur_w = [], [], 0.0
    for wd in words:
        f, ww, _, _ = measure(wd)
        sp = st["word_spacing"] * base_px
        add = ww + (sp if cur else 0)
        if cur and (len(cur) >= st["max_words_per_line"] or cur_w + add > maxw):
            lines.append(cur)
            cur, cur_w = [], 0.0
            add = ww
        cur.append(wd)
        cur_w += add
        if wd["br"]:
            lines.append(cur)
            cur, cur_w = [], 0.0
    if cur:
        lines.append(cur)

    placed, y, block_w = [], 0.0, 0.0
    kicker = None
    if seg.get("kicker"):
        kf = get_font(st["kicker_font"], st["kicker_size"] * W)
        ktxt = seg["kicker"].upper()
        kw = sum(kf.getlength(c) + st["kicker_tracking"] * kf.size for c in ktxt) - st["kicker_tracking"] * kf.size
        ka, kd = vmetrics(kf, True)
        kicker = {"text": ktxt, "font": kf, "w": kw, "h": ka + kd}
        y += (ka + kd) * 1.6
        block_w = kw
    for li, line in enumerate(lines):
        # natural width at k=1, then shrink/grow to fit
        def line_dims(k):
            ms = [measure(wd, k) for wd in line]
            sp = st["word_spacing"] * base_px * k
            return ms, sum(m[1] for m in ms) + sp * (len(ms) - 1), sp
        ms, lw, sp = line_dims(1.0)
        k = 1.0
        if st["fit_width"]:
            k = clamp(maxw / max(lw, 1), 0.4, 2.5)
        elif lw > maxw:
            k = maxw / lw
        if k != 1.0:
            ms, lw, sp = line_dims(k)
        asc = max(m[2] for m in ms)
        desc = max(m[3] for m in ms)
        lh = asc + desc
        if li > 0:
            y += lh * (st["line_spacing"] - 1.0)
        x = 0.0
        row = []
        for wd, (f, ww, a_, d_) in zip(line, ms):
            row.append(dict(wd, font=f, x=x, w=ww, base=y + asc, lh=lh, line=li))
            x += ww + sp
        for r in row:
            r["x"] -= lw / 2  # centred around 0
        placed.extend(row)
        y += lh
        block_w = max(block_w, lw)
    return {"words": placed, "w": block_w, "h": y, "kicker": kicker, "upper": upper, "has_box": has_box}


def load_captions(path):
    doc = json.loads(Path(path).read_text())
    segs = []
    for i, seg in enumerate(doc.get("segments", [])):
        if not seg.get("words"):
            continue
        st = style_for(seg, doc)
        s = float(seg.get("start", seg["words"][0]["s"]))
        e = float(seg.get("end", float(seg["words"][-1]["e"]) + st["hold"]))
        segs.append({"i": i, "seg": seg, "st": st, "start": s, "end": e,
                     "track": seg.get("preset") or doc.get("preset") or "pop"})
    # a caption disappears as soon as the next caption of the same track starts
    for sg in segs:
        nxt = [o["start"] for o in segs if o is not sg and o["track"] == sg["track"] and o["start"] > sg["start"]]
        sg["cut"] = min(nxt) if nxt else float("inf")
    return doc, segs


# ----------------------------------------------------------------------------- frame renderer
class Renderer:
    def __init__(self, segs, W, H, face, segmenter=None):
        self.segs, self.W, self.H, self.face, self.segmenter = segs, W, H, face, segmenter
        self.layouts = {}

    def block_origin(self, sg, lay, t):
        st, W, H = sg["st"], self.W, self.H
        bw, bh = lay["w"], lay["h"]
        ft = sg["start"] if st["follow"] == "lock" else t
        f = self.face.at(ft) if self.face else {"cx": 0.5, "top": 0.3, "bottom": 0.45, "w": 0.3}
        fh = f["bottom"] - f["top"]
        anchor = st["anchor"]
        if st.get("pos"):
            cx, cy = st["pos"][0] * W, st["pos"][1] * H
            top = cy - bh / 2
        elif anchor == "above_face":
            cx = W / 2 + (f["cx"] * W - W / 2) * st["follow_x"]
            head_top = (f["top"] - st["head_pad"] * fh) * H
            top = head_top - st["gap"] * H + st["overlap"] * bh - bh
        elif anchor == "below_face":
            cx = W / 2 + (f["cx"] * W - W / 2) * st["follow_x"]
            top = (f["bottom"] + 0.1 * fh) * H + st["gap"] * H
        elif anchor == "top":
            cx, top = W / 2, 0.12 * H
        elif anchor == "bottom":
            cx, top = W / 2, 0.80 * H - bh
        else:  # center
            cx, top = W / 2, H / 2 - bh / 2
        m = st["margin"] * W
        cx = clamp(cx, m + bw / 2, W - m - bw / 2) if bw < W - 2 * m else W / 2
        top = clamp(top, st["safe_top"] * H, max(st["safe_top"] * H, H * (1 - st["safe_bottom"]) - bh))
        return cx, top

    def anim(self, st, d, exit_q):
        """returns scale, alpha, dy_fraction_of_line"""
        p = clamp(d / max(st["anim_dur"], 1e-3))
        kind = st["anim"]
        scale, alpha, dy = 1.0, 1.0, 0.0
        if kind == "pop":
            scale = 0.45 + 0.55 * ease_out_back(p)
            alpha = clamp(d / 0.07)
        elif kind == "slam":
            scale = 1 + 0.4 * (1 - ease_out_cubic(p))
            alpha = clamp(d / 0.06)
        elif kind == "rise":
            dy = (1 - ease_out_cubic(p)) * 0.35
            alpha = ease_out_cubic(p)
        elif kind == "fade":
            alpha = p
        if exit_q > 0:
            alpha *= 1 - exit_q
            scale *= 1 - 0.08 * exit_q
        return scale, alpha, dy

    def render(self, t, frame=None):
        """Returns list of (canvas RGBA, behind_bool) or [] when nothing to draw."""
        out = []
        for sg in self.segs:
            st = sg["st"]
            if not (sg["start"] - 0.001 <= t < min(sg["end"] + st["exit_dur"], sg["cut"])):
                continue
            if sg["i"] not in self.layouts:
                self.layouts[sg["i"]] = layout(sg["seg"], st, self.W, self.H)
            lay = self.layouts[sg["i"]]
            canvas = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            cx, top = self.block_origin(sg, lay, t)
            exit_q = clamp((t - sg["end"]) / max(st["exit_dur"], 1e-3)) if t > sg["end"] else 0.0
            sh = st["shadow"] or None
            shadow = ({"blur": sh["blur"] * self.W, "dx": sh.get("dx", 0) * self.W,
                       "dy": sh.get("dy", 0) * self.W, "alpha": sh.get("alpha", 0.6)} if sh else None)
            # kicker
            if lay["kicker"]:
                k = lay["kicker"]
                sc, al, dy = self.anim(dict(st, anim="rise" if st["anim"] != "none" else "none"),
                                       t - sg["start"], exit_q)
                spr, (ox, oy, cw, chh) = word_sprite(k["text"], k["font"], True, hex_rgba(st["kicker_color"]),
                                                    shadow=shadow, tracking=st["kicker_tracking"])
                self.paste(canvas, spr, cx - cw / 2 - ox, top - oy + dy * k["h"], 1.0, al, (ox, oy, cw, chh))
            for wd in lay["words"]:
                d = t - wd["s"]
                active = wd["s"] <= t < wd["e"]
                if d < 0:
                    if st["upcoming"] != "dim":
                        continue
                    fill = hex_rgba(st["dim_color"], st["dim_alpha"])
                    box, glow, sc, al, dy = None, None, 1.0, 1.0 - exit_q, 0.0
                else:
                    color = st["color"]
                    if wd["emph"] and st["emph_color"]:
                        color = st["emph_color"]
                    if active and st["active_color"]:
                        color = st["active_color"]
                    box = (st["active_box"] if (active and st["active_box"]) else
                           st["emph_box"] if (wd["emph"] and st["emph_box"]) else st["spoken_box"])
                    if box and st["box_text_color"]:
                        color = st["box_text_color"]
                    fill = hex_rgba(color)
                    glow = st["emph_color"] if (wd["emph"] and st["emph_glow"] and st["emph_color"]) else None
                    sc, al, dy = self.anim(st, d, exit_q)
                padv = st["box_pad"] if lay["has_box"] else (0, 0)
                spr, (ox, oy, cw, chh) = word_sprite(
                    wd["text"], wd["font"], lay["upper"], fill, box=box, pad=st["box_pad"] if box else (0, 0),
                    radius=st["box_radius"], shadow=shadow, glow=glow,
                    stroke=int(st["stroke"] * wd["font"].size), stroke_fill=hex_rgba(st["stroke_color"]))
                # content box target (box layout reserves padding even for unboxed words)
                asc, _ = vmetrics(wd["font"], lay["upper"])
                padx = padv[0] * wd["font"].size if not box else 0
                pady = padv[1] * wd["font"].size if not box else 0
                x0 = cx + wd["x"] + padx
                y0 = top + wd["base"] - asc - (padv[1] * wd["font"].size if box else 0)
                self.paste(canvas, spr, x0 - ox, y0 - oy + dy * wd["lh"], sc, al, (ox, oy, cw, chh))
            out.append((canvas, bool(st["behind"]) and self.segmenter is not None))
        return out

    @staticmethod
    def paste(canvas, spr, x, y, scale, alpha, content):
        if alpha <= 0.003:
            return
        ox, oy, cw, ch = content
        if abs(scale - 1.0) > 0.003:
            nw, nh = max(1, int(spr.width * scale)), max(1, int(spr.height * scale))
            # scale around the content-box centre
            ccx, ccy = x + ox + cw / 2, y + oy + ch / 2
            spr = spr.resize((nw, nh), Image.BILINEAR)
            x = ccx - (ox + cw / 2) * scale
            y = ccy - (oy + ch / 2) * scale
        if alpha < 0.997:
            spr = spr.copy()
            spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
        x, y = int(round(x)), int(round(y))
        # clip to canvas
        sx0, sy0 = max(0, -x), max(0, -y)
        sx1, sy1 = min(spr.width, canvas.width - x), min(spr.height, canvas.height - y)
        if sx1 <= sx0 or sy1 <= sy0:
            return
        canvas.alpha_composite(spr.crop((sx0, sy0, sx1, sy1)), (x + sx0, y + sy0))


def composite(frame, layers, segmenter):
    """frame: HxWx3 uint8 (modified copy returned)."""
    if not layers:
        return frame
    f = frame.astype(np.float32)
    mask = None
    # behind layers first, then front
    for canvas, behind in sorted(layers, key=lambda l: not l[1]):
        bbox = canvas.getbbox()
        if not bbox:
            continue
        x0, y0, x1, y1 = bbox
        arr = np.asarray(canvas.crop(bbox), dtype=np.float32)
        a = arr[..., 3:4] / 255.0
        if behind:
            if mask is None:
                mask = segmenter.mask(frame)
            a = a * (1.0 - mask[y0:y1, x0:x1, None])
        f[y0:y1, x0:x1] = f[y0:y1, x0:x1] * (1 - a) + arr[..., :3] * a
    return np.clip(f + 0.5, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------- main
def get_face(video, W, H, dur, recompute=False, disable=False):
    if disable:
        return None
    cache = Path(str(video) + ".face.json")
    if cache.exists() and not recompute:
        tr = json.loads(cache.read_text())
        if tr.get("W") == W and tr.get("H") == H:
            return Face(tr)
    t0 = time.time()
    tr = track_faces(str(video), W, H, dur)
    tr["W"], tr["H"] = W, H
    try:
        cache.write_text(json.dumps(tr))
    except OSError:
        pass
    log(f"[face] tracked in {time.time() - t0:.1f}s (cuts at {', '.join(f'{c:.1f}s' for c in tr['cuts']) or 'none'})")
    return Face(tr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("captions")
    ap.add_argument("-o", "--out", help="output mp4 (default: <video>_captioned.mp4)")
    ap.add_argument("--preview", help="comma separated timestamps (s): write PNG stills instead of a video")
    ap.add_argument("--preview-dir", default=None)
    ap.add_argument("--fps", type=float, default=None, help="output fps (default: source)")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--preset", default="medium", help="x264 preset")
    ap.add_argument("--no-face", action="store_true", help="skip face tracking (centre layout)")
    ap.add_argument("--retrack", action="store_true", help="ignore cached face track")
    ap.add_argument("--no-behind", action="store_true", help="disable behind-the-head masking")
    ap.add_argument("--start", type=float, default=0.0, help="render only from this time (s)")
    ap.add_argument("--duration", type=float, default=None, help="render only this many seconds")
    a = ap.parse_args()

    W, H, fps, dur, has_audio = video_info(a.video)
    fps = a.fps or fps
    log(f"[video] {W}x{H} @ {fps:.3f}fps, {dur:.2f}s, audio={'yes' if has_audio else 'no'}")
    doc, segs = load_captions(a.captions)
    log(f"[captions] {len(segs)} segments")
    face = get_face(a.video, W, H, dur, a.retrack, a.no_face)

    segmenter = None
    if not a.no_behind and any(s["st"]["behind"] for s in segs):
        try:
            segmenter = Segmenter()
        except Exception as e:
            log(f"[behind] disabled ({e.__class__.__name__}: {e}). pip install mediapipe to enable.")
    R = Renderer(segs, W, H, face, segmenter)
    try:
        run(a, R, W, H, fps, dur, has_audio, segmenter)
    finally:
        if segmenter:
            segmenter.close()


def run(a, R, W, H, fps, dur, has_audio, segmenter):

    if a.preview:
        times = [float(x) for x in a.preview.split(",") if x.strip()]
        outdir = Path(a.preview_dir or (Path(a.video).with_suffix("").as_posix() + "_preview"))
        outdir.mkdir(parents=True, exist_ok=True)
        thumbs = []
        for t in times:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1",
                                  "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
            if len(raw) < W * H * 3:
                log(f"[preview] no frame at {t}s")
                continue
            fr = np.frombuffer(raw[:W * H * 3], np.uint8).reshape(H, W, 3)
            img = Image.fromarray(composite(fr, R.render(t), segmenter))
            p = outdir / f"preview_{t:07.2f}.png"
            img.save(p)
            thumbs.append((t, img))
            print(p)
        if thumbs:
            tw = 360
            th = int(H * tw / W)
            cols = min(4, len(thumbs))
            rows = math.ceil(len(thumbs) / cols)
            sheet = Image.new("RGB", (cols * tw, rows * (th + 28)), (20, 20, 20))
            dr = ImageDraw.Draw(sheet)
            for k, (t, img) in enumerate(thumbs):
                cx_, cy_ = (k % cols) * tw, (k // cols) * (th + 28)
                sheet.paste(img.resize((tw, th)), (cx_, cy_ + 28))
                dr.text((cx_ + 8, cy_ + 6), f"t={t:.2f}s", fill=(255, 255, 255), font=get_font("Poppins-SemiBold.ttf", 16))
            sp = outdir / "preview_sheet.jpg"
            sheet.save(sp, quality=88)
            print(sp)
        return

    out = a.out or (str(Path(a.video).with_suffix("")) + "_captioned.mp4")
    ss = ["-ss", f"{a.start:.3f}"] if a.start else []
    tt = ["-t", f"{a.duration:.3f}"] if a.duration else []
    dec = subprocess.Popen(["ffmpeg", "-v", "error", *ss, "-i", a.video, *tt, "-vf", f"fps={fps}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc_cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", f"{fps}", "-i", "-", *ss, "-i", a.video, *tt, "-map", "0:v:0"]
    if has_audio:
        enc_cmd += ["-map", "1:a:0", "-c:a", "aac", "-b:a", "192k"]
    enc_cmd += ["-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-preset", a.preset,
                "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-shortest", out]
    enc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE)
    n = W * H * 3
    i, t0, last = 0, time.time(), 0.0
    total = (a.duration or (dur - a.start)) * fps
    while True:
        buf = read_exact(dec.stdout, n)
        if len(buf) < n:
            break
        t = a.start + i / fps
        layers = R.render(t)
        if layers:
            buf = composite(np.frombuffer(buf, np.uint8).reshape(H, W, 3), layers, segmenter).tobytes()
        enc.stdin.write(buf)
        i += 1
        if time.time() - last > 3:
            last = time.time()
            log(f"[render] {i}/{int(total)} frames ({100 * i / max(total, 1):.0f}%), {i / (last - t0):.1f} fps")
    enc.stdin.close()
    dec.wait()
    rc = enc.wait()
    if rc != 0:
        raise SystemExit(f"ffmpeg encoder failed (exit {rc})")
    log(f"[done] {i} frames in {time.time() - t0:.1f}s -> {out}")
    print(out)


if __name__ == "__main__":
    os.environ.setdefault("GLOG_minloglevel", "2")
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    main()
