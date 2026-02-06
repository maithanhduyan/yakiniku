#!/usr/bin/env python3
"""
Pre-commit encoding check — prevents BOM, mojibake, and wrong encoding from being committed.

Usage:
    python scripts/check_encoding.py [directory]           # Check only (exit 1 if issues found)
    python scripts/check_encoding.py [directory] --fix     # Auto-fix issues

Exit codes:
    0 = all clean
    1 = issues found (use --fix to auto-fix)
"""
import io
import os
import sys
import subprocess

# Force UTF-8 stdout on Windows (git hooks use CP1252 by default)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Detect characters commonly produced by double-encoding UTF-8 through CP1252
MOJIBAKE_MARKERS = [
    "\xc3\x83",       # Ã followed by another control-like char
    "\xc2\xa0",       # Â followed by non-breaking space pattern
    "\xc3\xa2\xc2",   # â followed by Â — common in triple-encoded
    "\xc3\x85",       # Å
    "\xc3\x82",       # Â
    "\xc2\xad",       # Â­
]

# Suspicious codepoint ranges that indicate CP1252 misinterpretation
# These Unicode chars rarely appear in source code but are common in mojibake
SUSPICIOUS_CHARS = {
    '\u0152', '\u0153',  # Œ, œ
    '\u0160', '\u0161',  # Š, š
    '\u0178',            # Ÿ
    '\u017D', '\u017E',  # Ž, ž
    '\u0192',            # ƒ
    '\u02C6', '\u02DC',  # ˆ, ˜
}

TEXT_EXTENSIONS = {
    '.py', '.js', '.html', '.css', '.json', '.md', '.txt',
    '.yml', '.yaml', '.toml', '.cfg', '.ini', '.sql', '.sh',
    '.mako', '.env', '.gitignore', '.editorconfig',
}

# Files that contain encoding chars as literals (self-referencing)
SKIP_FILES = {
    'check_encoding.py',
    'fix_encoding.py',
}


def has_bom(raw: bytes) -> bool:
    return raw.startswith(b'\xef\xbb\xbf')


def has_mojibake(text: str) -> list[str]:
    """Detect mojibake patterns. Returns list of issues found."""
    issues = []
    for marker in MOJIBAKE_MARKERS:
        if marker in text:
            issues.append(f"mojibake pattern: {repr(marker)}")
            break  # One is enough to flag

    # Check for suspicious CP1252-range chars in non-French/non-Czech source code
    for ch in SUSPICIOUS_CHARS:
        if ch in text:
            # These chars are valid in some languages, but suspicious in our codebase
            issues.append(f"suspicious char U+{ord(ch):04X} ({ch})")
            break

    return issues


def has_crlf(raw: bytes) -> bool:
    return b'\r\n' in raw


def check_file(fpath: str) -> list[str]:
    """Check a single file for encoding issues. Returns list of issues."""
    issues = []
    try:
        with open(fpath, 'rb') as f:
            raw = f.read()
    except (OSError, IOError):
        return [f"cannot read file"]

    # 1. BOM check
    if has_bom(raw):
        issues.append("has UTF-8 BOM (should be plain UTF-8)")

    # 2. Valid UTF-8 check
    try:
        clean = raw[3:] if has_bom(raw) else raw
        text = clean.decode('utf-8')
    except UnicodeDecodeError as e:
        issues.append(f"not valid UTF-8: {e}")
        return issues

    # 3. Mojibake check
    mojibake = has_mojibake(text)
    issues.extend(mojibake)

    # 4. CRLF check (we enforce LF)
    if has_crlf(raw):
        issues.append("has CRLF line endings (should be LF)")

    return issues


def get_staged_files() -> list[str]:
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def scan_directory(directory: str) -> dict[str, list[str]]:
    """Scan all text files in directory. Returns {filepath: [issues]}."""
    results = {}
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in {
            '__pycache__', '.git', 'node_modules', '.venv', 'venv',
            '.mypy_cache', '.pytest_cache', '.ruff_cache',
        }]
        for fname in files:
            _, ext = os.path.splitext(fname)
            if ext.lower() not in TEXT_EXTENSIONS and fname not in {'.gitignore', '.editorconfig', '.env'}:
                continue
            if fname in SKIP_FILES:
                continue
            fpath = os.path.join(root, fname)
            issues = check_file(fpath)
            if issues:
                results[fpath] = issues
    return results


def main():
    args = sys.argv[1:]
    fix_mode = '--fix' in args
    git_mode = '--git-staged' in args
    args = [a for a in args if not a.startswith('--')]

    if git_mode:
        # Pre-commit hook mode: check only staged files
        staged = get_staged_files()
        text_staged = [
            f for f in staged
            if os.path.splitext(f)[1].lower() in TEXT_EXTENSIONS
            and os.path.basename(f) not in SKIP_FILES
        ]
        if not text_staged:
            sys.exit(0)

        results = {}
        for fpath in text_staged:
            if os.path.exists(fpath):
                issues = check_file(fpath)
                if issues:
                    results[fpath] = issues
    else:
        # Directory scan mode
        target = args[0] if args else '.'
        print(f"🔍 Scanning {target}/ for encoding issues...\n")
        results = scan_directory(target)

    if not results:
        if not git_mode:
            print("✅ All files clean — no encoding issues found.")
        sys.exit(0)

    # Report issues
    print(f"❌ Found encoding issues in {len(results)} file(s):\n")
    for fpath, issues in sorted(results.items()):
        for issue in issues:
            print(f"  {fpath}: {issue}")

    if fix_mode:
        print("\n🔧 Fixing issues...")
        # Import the fix tool
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, script_dir)
        from fix_encoding import fix_file

        fixed = 0
        for fpath in results:
            try:
                if fix_file(fpath, remove_bom=True):
                    print(f"  ✅ Fixed: {fpath}")
                    fixed += 1
            except Exception as e:
                print(f"  ❌ Failed: {fpath}: {e}")
        print(f"\nFixed {fixed}/{len(results)} files.")
    else:
        print(f"\n💡 Run with --fix to auto-fix: python scripts/check_encoding.py {args[0] if args else '.'} --fix")
        sys.exit(1)


if __name__ == '__main__':
    main()
