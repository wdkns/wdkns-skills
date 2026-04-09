#!/usr/bin/env python3
import argparse
import re
from dataclasses import dataclass
from pathlib import Path


TIME_RE = re.compile(
    r"(?P<sh>\d{2}):(?P<sm>\d{2}):(?P<ss>\d{2}),(?P<sms>\d{3})\s*-->\s*"
    r"(?P<eh>\d{2}):(?P<em>\d{2}):(?P<es>\d{2}),(?P<ems>\d{3})"
)
PUNCT_RE = re.compile(r"[，。！？；：、“”‘’（）《》〈〉【】〔〕—…,.!?;:'\"()\\[\\]{}<>/\\\\-]")
BASE_ID_RE = re.compile(r"^(\d+)")
FILLER_ONLY_RE = re.compile(r"^[嗯啊呃哈欸诶唉哎哦额恩]+$")


@dataclass
class Entry:
    block_id: str
    start_ms: int
    end_ms: int
    text: str


def parse_time(value: str) -> tuple[int, int]:
    match = TIME_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"bad time line: {value!r}")

    def pack(prefix: str) -> int:
        hour = int(match.group(f"{prefix}h"))
        minute = int(match.group(f"{prefix}m"))
        second = int(match.group(f"{prefix}s"))
        milli = int(match.group(f"{prefix}ms"))
        return (((hour * 60) + minute) * 60 + second) * 1000 + milli

    return pack("s"), pack("e")


def format_time(value: int) -> str:
    hour, rem = divmod(value, 3_600_000)
    minute, rem = divmod(rem, 60_000)
    second, milli = divmod(rem, 1000)
    return f"{hour:02d}:{minute:02d}:{second:02d},{milli:03d}"


def parse_srt(path: Path) -> list[Entry]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    entries: list[Entry] = []
    for block in blocks:
        lines = [line.rstrip() for line in block.splitlines()]
        if len(lines) < 3:
            raise ValueError(f"{path}: malformed block: {block!r}")
        block_id = lines[0].strip()
        start_ms, end_ms = parse_time(lines[1].strip())
        text_line = " ".join(line.strip() for line in lines[2:]).strip()
        entries.append(Entry(block_id=block_id, start_ms=start_ms, end_ms=end_ms, text=text_line))
    return entries


def base_id(block_id: str) -> int:
    match = BASE_ID_RE.match(block_id.strip())
    if not match:
        raise ValueError(f"bad block id: {block_id!r}")
    return int(match.group(1))


def parse_allowed_deletions(value: str) -> set[int]:
    if not value.strip():
        return set()
    result = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        result.add(int(part))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge cleaned SRT chunks into one renumbered SRT."
    )
    parser.add_argument("raw_srt", type=Path, help="Path to the raw source SRT")
    parser.add_argument("chunk_dir", type=Path, help="Directory containing clean_chunk_*.srt files")
    parser.add_argument("output_srt", type=Path, help="Path to the merged output SRT")
    parser.add_argument(
        "--allowed-deletions",
        default="",
        help="Comma-separated raw subtitle ids that are allowed to be deleted even if not filler-only",
    )
    args = parser.parse_args()

    raw_path = args.raw_srt
    chunk_dir = args.chunk_dir
    output_path = args.output_srt
    allowed_deletions = parse_allowed_deletions(args.allowed_deletions)

    raw_entries = parse_srt(raw_path)
    raw_map = {int(entry.block_id): entry for entry in raw_entries}

    clean_paths = sorted(chunk_dir.glob("clean_chunk_*.srt"))
    if not clean_paths:
        print("no clean chunks found", file=sys.stderr)
        return 1

    merged_entries: list[Entry] = []
    issues: list[str] = []
    deletions: list[int] = []

    for clean_path in clean_paths:
        clean_entries = parse_srt(clean_path)
        grouped: dict[int, list[Entry]] = {}
        for entry in clean_entries:
            grouped.setdefault(base_id(entry.block_id), []).append(entry)

            if not entry.text:
                issues.append(f"{clean_path.name} {entry.block_id}: empty text")
            if "\n" in entry.text:
                issues.append(f"{clean_path.name} {entry.block_id}: multiline text")
            if PUNCT_RE.search(entry.text):
                issues.append(f"{clean_path.name} {entry.block_id}: punctuation remains in {entry.text!r}")
            if len(entry.text.replace(" ", "")) > 14:
                issues.append(f"{clean_path.name} {entry.block_id}: text longer than 14 chars in {entry.text!r}")
            if entry.end_ms < entry.start_ms:
                issues.append(f"{clean_path.name} {entry.block_id}: negative duration")

        raw_chunk_ids = []
        raw_name_match = re.search(r"_(\d{4})-(\d{4})\.srt$", clean_path.name.replace("clean_chunk", "raw_chunk"))
        if raw_name_match:
            start_id = int(raw_name_match.group(1))
            end_id = int(raw_name_match.group(2))
            raw_chunk_ids = list(range(start_id, end_id + 1))

        for raw_id in raw_chunk_ids:
            if raw_id not in grouped:
                raw_text = raw_map[raw_id].text
                if raw_id not in allowed_deletions and not FILLER_ONLY_RE.fullmatch(raw_text.replace(" ", "")):
                    deletions.append(raw_id)
                continue

            original = raw_map[raw_id]
            parts = grouped[raw_id]
            parts.sort(key=lambda item: (item.start_ms, item.end_ms, item.block_id))
            prev_end = None
            for part in parts:
                if part.start_ms < original.start_ms or part.end_ms > original.end_ms:
                    issues.append(
                        f"{clean_path.name} {part.block_id}: outside original range "
                        f"{format_time(original.start_ms)} --> {format_time(original.end_ms)}"
                    )
                if prev_end is not None and part.start_ms < prev_end:
                    issues.append(f"{clean_path.name} {part.block_id}: overlaps previous split segment")
                prev_end = part.end_ms

            if len(parts) > 1:
                if parts[0].start_ms != original.start_ms:
                    issues.append(f"{clean_path.name} {raw_id}: split does not start at original boundary")
                if parts[-1].end_ms != original.end_ms:
                    issues.append(f"{clean_path.name} {raw_id}: split does not end at original boundary")
                for left, right in zip(parts, parts[1:]):
                    if left.end_ms != right.start_ms:
                        issues.append(f"{clean_path.name} {raw_id}: split segments are not edge-aligned")

            merged_entries.extend(parts)

    if deletions:
        issues.append(f"unexpected deletions: {', '.join(str(value) for value in deletions)}")

    merged_entries.sort(key=lambda item: item.start_ms)

    output_lines = []
    for index, entry in enumerate(merged_entries, start=1):
        output_lines.extend(
            [
                str(index),
                f"{format_time(entry.start_ms)} --> {format_time(entry.end_ms)}",
                entry.text,
                "",
            ]
        )
    output_path.write_text("\n".join(output_lines).rstrip() + "\n", encoding="utf-8")

    print(f"merged_chunks={len(clean_paths)}")
    print(f"merged_entries={len(merged_entries)}")
    print(f"allowed_deletions={sorted(allowed_deletions)}")
    print(f"output={output_path}")
    if issues:
        print("issues_found")
        for issue in issues:
            print(issue)
        return 2

    print("issues_found=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
