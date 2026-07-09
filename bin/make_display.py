#!/usr/bin/env python3
"""Generate display-res photos for the lightbox from full-res sources.

For every photo in assets/photography_lowres/<project>/ that has no file yet in
assets/photography_display/<project>/, this script:

  1. finds full-res candidates in the source folders by filename
     (extension-insensitive, " Large" suffix stripped),
  2. verifies the match by pixel content (12x12 thumbnail comparison via sips)
     and aspect ratio -- camera filenames recycle across shoots, so filename
     alone is NOT trustworthy,
  3. picks the highest-resolution verified copy,
  4. writes a 2560px-long-edge JPEG (q85) with EXIF/XMP/IPTC stripped
     (iPhone sources carry GPS; the ICC color profile is kept).

Photos whose source is missing or <= 2048px are skipped (the lightbox falls
back to the lowres file). Run from the repo root:

    python3 bin/make_display.py                 # all projects
    python3 bin/make_display.py best-friends    # one project
    python3 bin/make_display.py --dry           # report only
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOWRES = os.path.join(REPO, "assets/photography_lowres")
DISPLAY = os.path.join(REPO, "assets/photography_display")
SOURCES = [
    "/Volumes/T7/Pictures/2026_SF",
    "/Volumes/T7/Pictures/2025_SF_export",
]
TARGET = 2560          # long edge of generated display files
JPEG_QUALITY = "85"
MAE_MAX = 10           # 12x12 mean abs pixel diff; verified pairs score <7,
                       # different photos (even same-burst frames) score >14
ASPECT_TOL = 0.02
THUMB = 12
IMG_EXTS = (".jpg", ".jpeg", ".png")


# ---- minimal JPEG metadata handling (stdlib only) --------------------------

def _segments(data):
    """Yield (marker, start, end) for each JPEG segment up to SOS."""
    assert data[:2] == b"\xff\xd8", "not a JPEG"
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            raise ValueError(f"bad marker sync at {i}")
        marker = data[i + 1]
        if marker == 0xD8:
            i += 2
            continue
        if marker == 0xDA:  # SOS: rest is entropy data + EOI
            yield (marker, i, len(data))
            return
        length = struct.unpack_from(">H", data, i + 2)[0]
        yield (marker, i, i + 2 + length)
        i += 2 + length


def strip_metadata(path):
    """Drop EXIF/XMP/IPTC/comment segments; keep JFIF (APP0) + ICC (APP2)."""
    with open(path, "rb") as fh:
        data = fh.read()
    out = [b"\xff\xd8"]
    for marker, start, end in _segments(data):
        if marker in (0xE1, 0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9,
                      0xEA, 0xEB, 0xEC, 0xED, 0xEE, 0xEF, 0xFE):
            continue
        out.append(data[start:end])
    with open(path, "wb") as fh:
        fh.write(b"".join(out))


# ---- image inspection via sips ---------------------------------------------

def dims(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                         capture_output=True, text=True, timeout=30).stdout
    vals = [int(l.split(":")[1]) for l in out.splitlines() if "pixel" in l]
    return (vals[0], vals[1]) if len(vals) == 2 else None


def thumb_pixels(path, tmpdir, cache={}):
    """(r,g,b) list for a forced 12x12 resize; None if unreadable."""
    if path in cache:
        return cache[path]
    out = os.path.join(tmpdir, f"t_{len(cache)}.bmp")
    r = subprocess.run(
        ["sips", "-s", "format", "bmp", "-z", str(THUMB), str(THUMB), path, "--out", out],
        capture_output=True, timeout=60)
    pixels = None
    if r.returncode == 0 and os.path.exists(out):
        with open(out, "rb") as fh:
            data = fh.read()
        os.unlink(out)
        offset = struct.unpack_from("<I", data, 10)[0]
        w = struct.unpack_from("<i", data, 18)[0]
        h = struct.unpack_from("<i", data, 22)[0]
        bpp = struct.unpack_from("<H", data, 28)[0]
        if w == THUMB and abs(h) == THUMB and bpp in (24, 32):
            nbytes = bpp // 8
            rowsize = ((w * nbytes + 3) // 4) * 4
            rows = []
            for row in range(abs(h)):
                base = offset + row * rowsize
                rows.append([(data[base + c * nbytes + 2],
                              data[base + c * nbytes + 1],
                              data[base + c * nbytes]) for c in range(w)])
            if h > 0:
                rows.reverse()
            pixels = [p for row in rows for p in row]
    cache[path] = pixels
    return pixels


def mae(p1, p2):
    total = sum(abs(a - b) for px1, px2 in zip(p1, p2)
                for a, b in zip(px1, px2))
    return total / (len(p1) * 3)


# ---- matching + generation ---------------------------------------------------

def norm_key(filename):
    base = os.path.splitext(filename)[0]
    if base.endswith(" Large"):
        base = base[:-6]
    return base.lower()


def build_index():
    """key -> candidate source paths. jpg preferred over png; the shoots' own
    lowres/ and small/ subfolders are excluded."""
    jpgs, pngs = {}, {}
    for root_dir in SOURCES:
        for dirpath, _, filenames in os.walk(root_dir):
            parts = set(dirpath.split(os.sep))
            if "lowres" in parts or "small" in parts:
                continue
            for f in filenames:
                ext = os.path.splitext(f)[1].lower()
                if ext not in IMG_EXTS:
                    continue
                bucket = jpgs if ext != ".png" else pngs
                bucket.setdefault(norm_key(f), []).append(os.path.join(dirpath, f))
    index = dict(jpgs)
    for k, paths in pngs.items():
        index.setdefault(k, paths)
    return index


def generate(src, dest, src_long):
    if src_long > TARGET or src.lower().endswith(".png"):
        r = subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", JPEG_QUALITY,
             "-Z", str(TARGET), src, "--out", dest],
            capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip())
    else:
        shutil.copyfile(src, dest)
    strip_metadata(dest)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry = "--dry" in sys.argv
    projects = args or sorted(
        d for d in os.listdir(LOWRES)
        if os.path.isdir(os.path.join(LOWRES, d)))

    index = build_index()
    made, skipped = 0, []
    with tempfile.TemporaryDirectory() as tmpdir:
        for project in projects:
            pdir = os.path.join(LOWRES, project)
            for name in sorted(os.listdir(pdir)):
                if name.startswith(".") or \
                   os.path.splitext(name)[1].lower() not in IMG_EXTS:
                    continue
                dest = os.path.join(DISPLAY, project, name)
                if os.path.exists(dest):
                    continue
                lpath = os.path.join(pdir, name)
                cands = index.get(norm_key(name), [])
                ld = dims(lpath)
                lpx = thumb_pixels(lpath, tmpdir)
                if not cands or not ld or not lpx:
                    skipped.append((project, name, "no source candidate"))
                    continue
                passing = []
                for c in cands:
                    sd = dims(c)
                    spx = thumb_pixels(c, tmpdir)
                    if not sd or not spx:
                        continue
                    ar_off = abs(ld[0] / ld[1] - sd[0] / sd[1]) / (sd[0] / sd[1])
                    m = mae(lpx, spx)
                    if m <= MAE_MAX and ar_off <= ASPECT_TOL:
                        passing.append((max(sd), m, c))
                if not passing:
                    skipped.append((project, name,
                                    "no candidate matches by pixel content"))
                    continue
                passing.sort(reverse=True)
                src_long, m, src = passing[0]
                if src_long <= 2048:
                    skipped.append((project, name,
                                    f"source only {src_long}px (no gain)"))
                    continue
                if dry:
                    print(f"would make {project}/{name}  <- {src} ({src_long}px, mae={m:.1f})")
                else:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    generate(src, dest, src_long)
                    print(f"made {project}/{name}  <- {src}")
                made += 1

    print(f"\n{'would make' if dry else 'made'} {made}, skipped {len(skipped)}")
    for project, name, why in skipped:
        print(f"  skipped {project}/{name}: {why}")


if __name__ == "__main__":
    main()
