import re
from typing import Dict, Optional, Callable

from colors import green, yellow, red, underline

from daktari.check import CheckResult, CheckStatus
from daktari.os import OS, detect_os


def check_status_symbol(status: CheckStatus) -> str:
    return {
        CheckStatus.PASS: "✅",
        CheckStatus.PASS_WITH_WARNING: "⚠️ ",
        CheckStatus.FAIL: "❌",
    }[status]


def check_status_colour(status: CheckStatus) -> Callable:
    return {
        CheckStatus.PASS: green,
        CheckStatus.PASS_WITH_WARNING: yellow,
        CheckStatus.FAIL: red,
    }[status]


def get_most_specific_suggestion(this_os: str, suggestions: Dict[str, str]) -> Optional[str]:
    return suggestions.get(this_os, suggestions.get(OS.GENERIC))


def print_suggestion_text(text: str):
    pattern = re.compile("<cmd>(.+)</cmd>")

    def add_ansi_underline(match):
        return underline(match.group(1))

    replaced = pattern.sub(add_ansi_underline, text)
    lines = [line.lstrip() for line in replaced.splitlines()]

    raw_lines = [line.lstrip() for line in re.compile("</?cmd>").sub("", text).splitlines()]

    max_width = max([len(line) for line in raw_lines])
    title = "💡 Suggestion "
    print("┌─" + title + "─" * (max_width - len(title)) + "┐")
    for i, line in enumerate(lines):
        raw_line = raw_lines[i]
        padding = " " * (max_width - len(raw_line))
        print(f"│ {line}{padding} │")
    print("└" + "─" * (max_width + 2) + "┘")


def print_check_result(result: CheckResult):
    this_os = detect_os()
    status_symbol = check_status_symbol(result.status)
    colour = check_status_colour(result.status)
    print(f"{status_symbol} [{colour(result.name)}] {result.summary}")
    if result.status in (CheckStatus.FAIL, CheckStatus.PASS_WITH_WARNING):
        suggestion = get_most_specific_suggestion(this_os, result.suggestions)
        if suggestion:
            print_suggestion_text(suggestion)
