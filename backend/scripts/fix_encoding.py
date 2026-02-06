"""
Fix double-encoded UTF-8 mojibake in Python source files.

The issue: UTF-8 bytes were interpreted as CP1252 then re-encoded to UTF-8,
creating mojibake like 'å'¼ã\x81³å‡ºã\x81—' instead of '呼び出し'.

This script reverses the process by mapping each Unicode codepoint back to
its CP1252 byte value, then decoding the resulting bytes as UTF-8.
"""
import os
import sys

# CP1252 extended range: codepoints that map to bytes 0x80-0x9F
# (These bytes are undefined in ISO-8859-1 but defined in CP1252)
CP1252_MAP = {
    0x20AC: 0x80,  # €
    0x201A: 0x82,  # ‚
    0x0192: 0x83,  # ƒ
    0x201E: 0x84,  # „
    0x2026: 0x85,  # …
    0x2020: 0x86,  # †
    0x2021: 0x87,  # ‡
    0x02C6: 0x88,  # ˆ
    0x2030: 0x89,  # ‰
    0x0160: 0x8A,  # Š
    0x2039: 0x8B,  # ‹
    0x0152: 0x8C,  # Œ
    0x017D: 0x8D,  # Ž (CP1252 only, not in Windows-1252 standard but used)
    0x2018: 0x91,  # '
    0x2019: 0x92,  # '
    0x201C: 0x93,  # "
    0x201D: 0x94,  # "
    0x2022: 0x95,  # •
    0x2013: 0x96,  # –
    0x2014: 0x97,  # —
    0x02DC: 0x98,  # ˜
    0x2122: 0x99,  # ™
    0x0161: 0x9A,  # š
    0x203A: 0x9B,  # ›
    0x0153: 0x9C,  # œ
    0x017E: 0x9E,  # ž
    0x0178: 0x9F,  # Ÿ
}


def char_to_byte(ch: str) -> int | None:
    """Convert a unicode char to its CP1252 byte value."""
    cp = ord(ch)
    if cp < 256:
        return cp
    return CP1252_MAP.get(cp, None)


def fix_mojibake(text: str) -> str:
    """Fix double-encoded UTF-8 by converting non-ASCII clusters back to bytes."""
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        cp = ord(ch)
        if cp < 128:
            result.append(ch)
            i += 1
            continue

        # Collect non-ASCII cluster
        cluster_start = i
        byte_list = []
        valid = True
        while i < len(text) and ord(text[i]) >= 128:
            b = char_to_byte(text[i])
            if b is None:
                valid = False
                break
            byte_list.append(b)
            i += 1

        if valid and byte_list:
            raw_bytes = bytes(byte_list)
            try:
                decoded = raw_bytes.decode("utf-8")
                result.append(decoded)
            except UnicodeDecodeError:
                # Not valid UTF-8 after conversion — keep original
                result.append(text[cluster_start:i])
        else:
            # Could not convert — keep original chars up to failure point
            # CRITICAL: advance i past the unconvertible char to avoid infinite loop
            if i == cluster_start:
                result.append(text[i])
                i += 1
            else:
                result.append(text[cluster_start:i])

    return "".join(result)


def strip_bom(raw: bytes) -> bytes:
    """Strip UTF-8 BOM if present."""
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:]
    return raw


def fix_file(fpath: str, remove_bom: bool = True, fix_crlf: bool = True) -> bool:
    """Fix encoding in a single file. Returns True if changes were made."""
    with open(fpath, "rb") as f:
        raw = f.read()

    had_bom = raw.startswith(b"\xef\xbb\xbf")
    had_crlf = b"\r\n" in raw
    clean_raw = strip_bom(raw) if remove_bom else raw
    text = clean_raw.decode("utf-8")

    fixed = fix_mojibake(text)

    # Normalize CRLF → LF
    if fix_crlf:
        fixed = fixed.replace("\r\n", "\n")

    changed = fixed != text or (remove_bom and had_bom) or (fix_crlf and had_crlf)

    if changed:
        with open(fpath, "w", encoding="utf-8", newline="") as f:
            f.write(fixed)
    return changed


def scan_and_fix(directory: str):
    """Scan directory for .py files with encoding issues and fix them."""
    fixed_count = 0
    bom_count = 0
    crlf_count = 0
    checked = 0

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            checked += 1

            with open(fpath, "rb") as f:
                raw = f.read()

            had_bom = raw.startswith(b"\xef\xbb\xbf")
            had_crlf = b"\r\n" in raw
            clean = strip_bom(raw)
            text = clean.decode("utf-8")
            fixed = fix_mojibake(text)
            fixed = fixed.replace("\r\n", "\n")

            bom_removed = had_bom
            content_changed = fixed != text
            crlf_fixed = had_crlf

            if bom_removed or content_changed or crlf_fixed:
                with open(fpath, "w", encoding="utf-8", newline="") as f:
                    f.write(fixed)

                status = []
                if content_changed and not (had_crlf and fixed == text.replace("\r\n", "\n")):
                    status.append("MOJIBAKE fixed")
                    fixed_count += 1
                if bom_removed:
                    status.append("BOM removed")
                    bom_count += 1
                if crlf_fixed:
                    status.append("CRLF→LF")
                    crlf_count += 1
                print(f"  ✅ {fpath}: {', '.join(status)}")

    print(f"\nSummary: checked {checked} files, fixed {fixed_count} mojibake, removed {bom_count} BOMs, normalized {crlf_count} CRLF→LF")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "app"
    print(f"Scanning {target}/ for encoding issues...\n")
    scan_and_fix(target)
