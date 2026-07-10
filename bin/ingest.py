#!/usr/bin/env python3
"""One-export photo pipeline: full-res picks in, grid + display + YAML stub out.

You export each photo from Lightroom exactly once (full resolution, into the
usual dated shoot folder). This tool takes your picks and generates everything
the site needs:

  assets/photography_lowres/<project>/<name>    2048px long edge (grid)
  assets/photography_display/<project>/<name>   2560px long edge (lightbox),
                                                only when the source is larger
                                                than 2048px
  _data/photography/<project>.yml               stub entry with the capture
                                                date from EXIF and a blank
                                                location for `bin/photos
                                                caption` to fill

All generated files are JPEG q85 with EXIF/XMP/IPTC stripped (several iPhone
exports carry GPS coordinates; the ICC color profile is kept) and EXIF
rotation baked into the pixels. PNG/HEIC sources are converted to JPEG.

Usage:
    python3 bin/ingest.py                      # inbox mode (see below)
    python3 bin/ingest.py <project> <file|dir ...>
    python3 bin/ingest.py --dry ...            # preview only

Inbox mode processes everything staged under /Volumes/T7/Pictures/picks/
(one subfolder per project -- created automatically, drag picks in with
Finder) and deletes each staged copy after verifying the generated files.
Path mode never deletes sources.

After ingesting, run:  bundle exec ruby bin/photos caption <project>
"""
import os
import re
import shutil
import struct
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_display import strip_metadata, dims

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOWRES_ROOT = os.path.join(REPO, "assets/photography_lowres")
DISPLAY_ROOT = os.path.join(REPO, "assets/photography_display")
DATA_DIR = os.path.join(REPO, "_data/photography")
INBOX = "/Volumes/T7/Pictures/picks"

GRID_TARGET = 2048
DISPLAY_TARGET = 2560
QUALITY = "85"
PLACEHOLDER_DATE = "2026-01-01"  # bin/photos' placeholder; fix-dates targets it
SOURCE_EXTS = (".jpg", ".jpeg", ".png", ".heic")
# EXIF orientation -> degrees clockwise to bake in (mirrored variants warned)
ORIENT_ROTATE = {3: 180, 6: 90, 8: 270}


def read_orientation(path):
    """EXIF orientation tag from a JPEG (1 if absent/unreadable)."""
    if not path.lower().endswith((".jpg", ".jpeg")):
        return 1
    with open(path, "rb") as fh:
        data = fh.read(256 * 1024)
    try:
        if data[:2] != b"\xff\xd8":
            return 1
        i = 2
        while i < len(data) - 4:
            if data[i] != 0xFF:
                return 1
            marker = data[i + 1]
            if marker == 0xDA:
                return 1
            length = struct.unpack_from(">H", data, i + 2)[0]
            if marker == 0xE1 and data[i + 4:i + 10] == b"Exif\x00\x00":
                t = i + 10
                endian = "<" if data[t:t + 2] == b"II" else ">"
                ifd = t + struct.unpack_from(endian + "I", data, t + 4)[0]
                n = struct.unpack_from(endian + "H", data, ifd)[0]
                for k in range(n):
                    e = ifd + 2 + k * 12
                    if struct.unpack_from(endian + "H", data, e)[0] == 0x0112:
                        return struct.unpack_from(endian + "H", data, e + 8)[0]
                return 1
            i += 2 + length
    except Exception:
        pass
    return 1


def _jpeg_date_time_original(path):
    """DateTimeOriginal (0x9003) from a JPEG's Exif sub-IFD, or None."""
    if not path.lower().endswith((".jpg", ".jpeg")):
        return None
    with open(path, "rb") as fh:
        data = fh.read(256 * 1024)
    try:
        if data[:2] != b"\xff\xd8":
            return None
        i = 2
        while i < len(data) - 4:
            if data[i] != 0xFF:
                return None
            marker = data[i + 1]
            if marker == 0xDA:
                return None
            length = struct.unpack_from(">H", data, i + 2)[0]
            if marker == 0xE1 and data[i + 4:i + 10] == b"Exif\x00\x00":
                t = i + 10
                endian = "<" if data[t:t + 2] == b"II" else ">"
                ifd = t + struct.unpack_from(endian + "I", data, t + 4)[0]
                n = struct.unpack_from(endian + "H", data, ifd)[0]
                for k in range(n):
                    e = ifd + 2 + k * 12
                    if struct.unpack_from(endian + "H", data, e)[0] == 0x8769:
                        sub = t + struct.unpack_from(endian + "I", data, e + 8)[0]
                        m = struct.unpack_from(endian + "H", data, sub)[0]
                        for j in range(m):
                            se = sub + 2 + j * 12
                            if struct.unpack_from(endian + "H", data, se)[0] == 0x9003:
                                off = t + struct.unpack_from(endian + "I", data, se + 8)[0]
                                raw = data[off:off + 19].decode("ascii", "replace")
                                dm = re.match(r"(\d{4}):(\d{2}):(\d{2})", raw)
                                if dm:
                                    return f"{dm.group(1)}-{dm.group(2)}-{dm.group(3)}"
                        return None
                return None
            i += 2 + length
    except Exception:
        pass
    return None


def exif_date(path):
    """Capture date as YYYY-MM-DD, or None.

    JPEGs: EXIF DateTimeOriginal or nothing — sips' `creation` property
    is deliberately NOT used (Lightroom exports carry the export
    timestamp there), and Spotlight falls back to the filesystem date
    for EXIF-less files, which would stamp a plausible-but-wrong date.
    Non-JPEG (HEIC): Spotlight's content-creation date, reported in UTC,
    so a late-evening shot can land on the next calendar day.
    """
    if path.lower().endswith((".jpg", ".jpeg")):
        return _jpeg_date_time_original(path)
    try:
        out = subprocess.run(
            ["mdls", "-name", "kMDItemContentCreationDate", "-raw", path],
            capture_output=True, text=True, timeout=30).stdout
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", out)
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    except Exception:
        pass
    return None


def filename_date(name):
    """Date embedded in phone-style filenames (IMG_YYYYMMDD_HHMMSS)."""
    m = re.search(r"(\d{4})(\d{2})(\d{2})_\d{6}", name)
    if m and 2000 <= int(m.group(1)) <= 2100:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def make_size(src, dest, target, rotate_deg):
    """Write dest as JPEG q85 <= target px long edge, rotated, stripped."""
    w, h = dims(src)
    needs_convert = not src.lower().endswith((".jpg", ".jpeg"))
    if max(w, h) > target:
        cmd = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", QUALITY,
               "-Z", str(target), src, "--out", dest]
    elif needs_convert:
        cmd = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", QUALITY,
               src, "--out", dest]
    else:
        shutil.copyfile(src, dest)
        cmd = None
    if cmd:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip())
    if rotate_deg:
        r = subprocess.run(["sips", "-r", str(rotate_deg), dest],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.strip())
    strip_metadata(dest)


def yaml_stub(project, filename, date):
    """Append a stub entry (blank location) unless the filename is present."""
    path = os.path.join(DATA_DIR, f"{project}.yml")
    if os.path.exists(path):
        with open(path) as fh:
            content = fh.read()
        if re.search(rf"^- filename:\s*{re.escape(filename)}\s*$",
                     content, re.MULTILINE):
            return False
        sep = "" if content.endswith("\n\n") or not content else "\n"
    else:
        sep = ""
        content = None
    with open(path, "a") as fh:
        fh.write(f'{sep}- filename: {filename}\n  location: ""\n  date: {date}\n')
    return True


def ingest_one(project, src, dry=False, delete_after=False):
    name = os.path.basename(src)
    stem, ext = os.path.splitext(name)
    if ext.lower() not in (".jpg", ".jpeg"):
        name = stem + ".jpg"

    lowres_dest = os.path.join(LOWRES_ROOT, project, name)
    display_dest = os.path.join(DISPLAY_ROOT, project, name)
    if os.path.exists(lowres_dest):
        print(f"  skip {project}/{name}: already in portfolio")
        return False

    d = dims(src)
    if not d:
        print(f"  skip {project}/{name}: unreadable image")
        return False
    long_edge = max(d)
    wants_display = long_edge > GRID_TARGET

    date = exif_date(src) or filename_date(name) or PLACEHOLDER_DATE
    orientation = read_orientation(src)
    rotate_deg = ORIENT_ROTATE.get(orientation, 0)
    if orientation in (2, 4, 5, 7):
        print(f"  warn {project}/{name}: mirrored EXIF orientation "
              f"{orientation}, check the result visually")

    if dry:
        print(f"  would ingest {project}/{name}: {long_edge}px source, "
              f"grid{' + display' if wants_display else ' only'}, date {date}"
              f"{' (placeholder)' if date == PLACEHOLDER_DATE else ''}")
        return True

    os.makedirs(os.path.dirname(lowres_dest), exist_ok=True)
    make_size(src, lowres_dest, GRID_TARGET, rotate_deg)
    if wants_display:
        os.makedirs(os.path.dirname(display_dest), exist_ok=True)
        make_size(src, display_dest, DISPLAY_TARGET, rotate_deg)
    stub_added = yaml_stub(project, name, date)

    ok = dims(lowres_dest) is not None and os.path.getsize(lowres_dest) > 0
    if wants_display:
        ok = ok and dims(display_dest) is not None \
             and os.path.getsize(display_dest) > 0
    if not ok:
        raise RuntimeError(f"{project}/{name}: generated files failed "
                           "verification, staged source kept")
    if delete_after:
        os.remove(src)

    print(f"  ingested {project}/{name} "
          f"(grid{' + display' if wants_display else ''}, date {date}"
          f"{', yaml stub' if stub_added else ''})")
    return True


def known_projects():
    return sorted(
        d for d in os.listdir(LOWRES_ROOT)
        if os.path.isdir(os.path.join(LOWRES_ROOT, d)))


def source_files(path):
    if os.path.isdir(path):
        return [os.path.join(path, f) for f in sorted(os.listdir(path))
                if not f.startswith(".")
                and os.path.splitext(f)[1].lower() in SOURCE_EXTS]
    return [path]


def main():
    dry = "--dry" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    count = 0

    if not args:
        # inbox mode
        os.makedirs(INBOX, exist_ok=True)
        for p in known_projects():
            os.makedirs(os.path.join(INBOX, p), exist_ok=True)
        staged = []
        for p in sorted(os.listdir(INBOX)):
            pdir = os.path.join(INBOX, p)
            if not os.path.isdir(pdir):
                continue
            if p not in known_projects():
                files = source_files(pdir)
                if files:
                    print(f"  warn: unknown project '{p}' in inbox "
                          f"({len(files)} file(s) NOT ingested)")
                continue
            staged.extend((p, f) for f in source_files(pdir))
        if not staged:
            print(f"inbox empty -- drag full-res picks into {INBOX}/<project>/")
            return
        for project, src in staged:
            if ingest_one(project, src, dry=dry, delete_after=True):
                count += 1
    else:
        project = args[0]
        if project not in known_projects():
            sys.exit(f"unknown project '{project}' -- known: "
                     f"{', '.join(known_projects())}")
        if len(args) < 2:
            sys.exit("usage: python3 bin/ingest.py <project> <file|dir ...>")
        for arg in args[1:]:
            if not os.path.exists(arg):
                sys.exit(f"no such file: {arg}")
            for src in source_files(arg):
                if ingest_one(project, src, dry=dry, delete_after=False):
                    count += 1

    if count and not dry:
        print(f"\n{count} photo(s) ingested. Next: "
              "bundle exec ruby bin/photos caption")


if __name__ == "__main__":
    main()
