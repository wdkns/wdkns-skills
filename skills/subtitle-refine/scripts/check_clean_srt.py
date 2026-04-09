#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
from difflib import SequenceMatcher
import re
from pathlib import Path

TIME_RE = re.compile(
    r"(?P<sh>\d{2}):(?P<sm>\d{2}):(?P<ss>\d{2}),(?P<sms>\d{3})\s*-->\s*"
    r"(?P<eh>\d{2}):(?P<em>\d{2}):(?P<es>\d{2}),(?P<ems>\d{3})"
)
PUNCT_RE = re.compile(r"[，。！？；：、“”‘’（）《》〈〉【】〔〕—…,.!?;:'\"()\[\]{}<>/\\-]")
FILLER_ONLY_RE = re.compile(r"^[嗯啊呃哈欸诶唉哎哦额恩]+$")


FILLER_CHARS = "嗯啊呃哈欸诶唉哎哦额恩"
SHORT_STUTTER_CHARS = "我你他她它这那哪有很都也就再会想要去来从把被跟和在说让给得的地"
FILLER_EDGE_RE = re.compile(rf"^(?:[{FILLER_CHARS}]{{1,2}}).+|.+(?:[{FILLER_CHARS}]{{1,2}})$")
SUFFIX_PAUSE_RE = re.compile(r"(?<! )(是吧|对吧|对吗|行吧|行吗|是不是|对不对)$")
PREFIX_PAUSE_RE = re.compile(r"^(来)(?=[那你我他她它咱先就吧呢啊呀])")
LATIN_WORD_RE = re.compile(r"[A-Za-z0-9]+|[^\sA-Za-z0-9]")
VALID_AA_PREFIXES = {
    "爸爸",
    "妈妈",
    "爷爷",
    "奶奶",
    "哥哥",
    "姐姐",
    "妹妹",
    "弟弟",
    "叔叔",
    "伯伯",
    "姑姑",
    "舅舅",
    "谢谢",
    "看看",
    "想想",
    "说说",
    "听听",
    "试试",
    "走走",
    "聊聊",
    "问问",
    "找找",
}
EDGE_FILLER_CHARS = FILLER_CHARS + "呀"


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


def compact_text(text: str) -> str:
    return text.replace(" ", "")


def visible_length(text: str, latin_word_as_one_char: bool) -> int:
    if latin_word_as_one_char:
        return len(LATIN_WORD_RE.findall(text))
    return len(compact_text(text))


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


def find_filler_signal(text: str) -> str | None:
    for token in text.split():
        if FILLER_ONLY_RE.fullmatch(token):
            return token

    compact = text.replace(" ", "")
    if FILLER_EDGE_RE.fullmatch(compact):
        return compact
    return None


def find_repeat_signal(text: str) -> str | None:
    tokens = text.split()
    for token in tokens:
        if len(token) >= 2 and token[:2] in VALID_AA_PREFIXES:
            continue
        if len(token) >= 3 and token[0] == token[1]:
            return token
        if len(token) == 2 and token[0] == token[1] and token[0] in SHORT_STUTTER_CHARS:
            return token

    for left, right in zip(tokens, tokens[1:]):
        if left == right and len(left) <= 2:
            return f"{left} {right}"

    return None


def find_pause_signal(text: str) -> str | None:
    compact = text.replace(" ", "")
    prefix_match = PREFIX_PAUSE_RE.search(compact)
    if prefix_match:
        return f"prefix:{prefix_match.group(1)}"

    suffix_match = SUFFIX_PAUSE_RE.search(text)
    if suffix_match:
        return f"suffix:{suffix_match.group(1)}"

    return None


def collapse_short_stutters(text: str) -> str:
    if not text:
        return text

    result: list[str] = []
    for char in text:
        if result and result[-1] == char and char in SHORT_STUTTER_CHARS:
            continue
        result.append(char)
    return "".join(result)


def collapse_repeated_prefix_chunks(text: str) -> str:
    current = text
    while current:
        max_chunk = min(4, len(current) // 2)
        collapsed = None
        for size in range(max_chunk, 0, -1):
            chunk = current[:size]
            if current.startswith(chunk * 2):
                collapsed = chunk + current[size * 2 :]
                break
        if collapsed is None or collapsed == current:
            return current
        current = collapsed
    return current


def conservative_normalize(text: str) -> str:
    compact = compact_text(text)
    compact = compact.lower()
    compact = re.sub(rf"^[{EDGE_FILLER_CHARS}]+", "", compact)
    compact = re.sub(rf"[{EDGE_FILLER_CHARS}]+$", "", compact)
    compact = collapse_short_stutters(compact)
    compact = collapse_repeated_prefix_chunks(compact)
    compact = re.sub(rf"^[{EDGE_FILLER_CHARS}]+", "", compact)
    compact = re.sub(rf"[{EDGE_FILLER_CHARS}]+$", "", compact)
    return compact


def text_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, compact_text(left), compact_text(right)).ratio()


def find_text_drift_signal(raw_text: str, clean_text: str) -> str | None:
    if compact_text(raw_text) == compact_text(clean_text):
        return None

    if conservative_normalize(raw_text) == conservative_normalize(clean_text):
        return None

    ratio = text_similarity(raw_text, clean_text)
    if ratio <= 0.45:
        return f"possible aggressive rewrite ({ratio:.2f}) -> raw={raw_text!r} clean={clean_text!r}"
    return None


def find_neighbor_shift_signal(raw_entries: list, index: int, clean_text: str) -> str | None:
    current = raw_entries[index].text
    current_ratio = text_similarity(current, clean_text)

    candidates: list[tuple[str, str, float]] = []
    if index > 0:
        candidates.append(("prev", raw_entries[index - 1].text, text_similarity(raw_entries[index - 1].text, clean_text)))
    if index + 1 < len(raw_entries):
        candidates.append(("next", raw_entries[index + 1].text, text_similarity(raw_entries[index + 1].text, clean_text)))

    for label, neighbor_text, neighbor_ratio in candidates:
        if neighbor_ratio >= 0.72 and neighbor_ratio >= current_ratio + 0.20:
            return (
                f"possible text carryover from {label} raw subtitle "
                f"(self={current_ratio:.2f}, {label}={neighbor_ratio:.2f}) -> {clean_text!r}"
            )
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a cleaned SRT against the raw SRT for timing and text constraints."
    )
    parser.add_argument("raw_srt", type=Path, help="Path to the raw source SRT")
    parser.add_argument("clean_srt", type=Path, help="Path to the cleaned SRT")
    parser.add_argument(
        "--allowed-deletions",
        default="",
        help="Comma-separated raw subtitle ids that are allowed to be deleted even if not filler-only",
    )
    parser.add_argument(
        "--min-duration-ms",
        type=int,
        default=400,
        help="Warn when a cleaned subtitle duration is shorter than this threshold",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Return a non-zero exit code when heuristic warnings are found",
    )
    parser.add_argument(
        "--latin-word-as-one-char",
        action="store_true",
        help="Count each contiguous Latin alnum token as one visible character for length checks",
    )
    args = parser.parse_args()

    raw_entries = parse_srt(args.raw_srt)
    clean_entries = parse_srt(args.clean_srt)
    allowed_deletions = parse_allowed_deletions(args.allowed_deletions)
    issues: list[str] = []
    warnings: list[str] = []
    grouped: dict[int, list] = {int(entry.block_id): [] for entry in raw_entries}

    for entry in clean_entries:
        text = entry.text
        if not text:
            issues.append(f"{entry.block_id}: empty text")
        if "\n" in text:
            issues.append(f"{entry.block_id}: multiline text")
        if PUNCT_RE.search(text):
            issues.append(f"{entry.block_id}: punctuation remains in {text!r}")
        if visible_length(text, args.latin_word_as_one_char) > 14:
            issues.append(f"{entry.block_id}: text longer than 14 chars in {text!r}")
        if entry.end_ms < entry.start_ms:
            issues.append(f"{entry.block_id}: negative duration")
        if entry.end_ms - entry.start_ms < args.min_duration_ms:
            warnings.append(
                f"{entry.block_id}: short duration {entry.end_ms - entry.start_ms}ms in {text!r}"
            )

        filler_signal = find_filler_signal(text)
        if filler_signal:
            warnings.append(f"{entry.block_id}: possible filler residue -> {filler_signal!r}")

        repeat_signal = find_repeat_signal(text)
        if repeat_signal:
            warnings.append(f"{entry.block_id}: possible repeated stutter residue -> {repeat_signal!r}")

        pause_signal = find_pause_signal(text)
        if pause_signal:
            warnings.append(f"{entry.block_id}: possible missing pause space -> {pause_signal} in {text!r}")

    raw_index = 0
    for entry in sorted(clean_entries, key=lambda item: (item.start_ms, item.end_ms, item.block_id)):
        while raw_index < len(raw_entries) and raw_entries[raw_index].end_ms <= entry.start_ms:
            raw_index += 1

        if raw_index >= len(raw_entries):
            issues.append(f"{entry.block_id}: starts after the last raw subtitle")
            continue

        owner = raw_entries[raw_index]
        if entry.start_ms < owner.start_ms or entry.end_ms > owner.end_ms:
            issues.append(f"{entry.block_id}: outside original range")
            continue

        grouped[int(owner.block_id)].append(entry)

    for index, original in enumerate(raw_entries):
        raw_id = int(original.block_id)
        parts = grouped[raw_id]
        if not parts:
            raw_text = original.text.replace(" ", "")
            if raw_id not in allowed_deletions and not FILLER_ONLY_RE.fullmatch(raw_text):
                issues.append(f"{raw_id}: deleted but not filler-only -> {original.text!r}")
            continue

        prev_end = None
        for part in parts:
            if prev_end is not None and part.start_ms < prev_end:
                issues.append(f"{part.block_id}: overlaps previous split segment")
            prev_end = part.end_ms

        if len(parts) == 1:
            only_part = parts[0]
            if only_part.start_ms != original.start_ms or only_part.end_ms != original.end_ms:
                issues.append(f"{raw_id}: unsplit subtitle timing changed")
            else:
                drift_signal = find_text_drift_signal(original.text, only_part.text)
                if drift_signal:
                    warnings.append(f"{raw_id}: {drift_signal}")

                shift_signal = find_neighbor_shift_signal(raw_entries, index, only_part.text)
                if shift_signal:
                    warnings.append(f"{raw_id}: {shift_signal}")

        if len(parts) > 1:
            if parts[0].start_ms != original.start_ms:
                issues.append(f"{raw_id}: split does not start at original boundary")
            if parts[-1].end_ms != original.end_ms:
                issues.append(f"{raw_id}: split does not end at original boundary")
            for left, right in zip(parts, parts[1:]):
                if left.end_ms != right.start_ms:
                    issues.append(f"{raw_id}: split segments are not edge-aligned")

    previous_start = None
    for entry in sorted(clean_entries, key=lambda item: (item.start_ms, item.end_ms, item.block_id)):
        if previous_start is not None and entry.start_ms < previous_start:
            issues.append(f"{entry.block_id}: global order issue")
        previous_start = entry.start_ms

    print(f"raw_entries={len(raw_entries)}")
    print(f"clean_entries={len(clean_entries)}")
    print(f"allowed_deletions={sorted(allowed_deletions)}")
    print(f"issues={len(issues)}")
    print(f"warnings={len(warnings)}")
    for issue in issues:
        print(issue)
    for warning in warnings:
        print(f"warning: {warning}")

    if issues:
        return 2
    if warnings and args.fail_on_warnings:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
